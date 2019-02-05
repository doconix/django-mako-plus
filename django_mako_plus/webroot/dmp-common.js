// note that I'm intentionally using older JS syntax for wide audience of browsers.
// I may rewrite this in modern JS at some point and transpile backwards, but smaller this way for now.
(function() {

    if (!window.DMP_CONTEXT) {
        window.DMP_CONTEXT = {
            __version__: '5.9.13',   // DMP version to check for mismatches
            contexts: {},           // id -> context1
            contextsByName: {},     // app/template -> [ context1, context2, ... ]
            lastContext: null,      // last inserted context (see getAll() below)
            templateFunctions: {},  // functions that wrap template JS/CSS (see DMP's webpack docs)
            logEnabled: null,       // whether the log is DEBUG in settings

            /* Adds data to the DMP context under the given key */
            set: function(context) {
                DMP_CONTEXT.logEnabled = context.log || DMP_CONTEXT.logEnabled;
                if (DMP_CONTEXT.__version__ != context.version) {
                    DMP_CONTEXT.log(['server version', context.version, 'is different from dmp-common.js', DMP_CONTEXT.__version__, '- unexpected behavior may occur']);
                }
                context.pendingCalls = 0;

                // link the id to the context
                DMP_CONTEXT.contexts[context.id] = context;
                DMP_CONTEXT.lastContext = context;

                // reverse lookups by name to context
                for (var i = 0; i < context.templates.length; i++) {
                    var tname = context.templates[i];
                    if (typeof DMP_CONTEXT.contextsByName[tname] === "undefined") {
                        DMP_CONTEXT.contextsByName[tname] = [];
                    }
                    DMP_CONTEXT.contextsByName[tname].push(context);
                }

                DMP_CONTEXT.log([ context.id, '-', 'created context' ], context);
            },

            /*
                Retrieves context data. If multiple script contexts are found, such as when ajax retrieves
                the same template snippet multiple times, the last one is returned.

                    DMP_CONTEXT.get()                                           // for the currently-executing script
                    DMP_CONTEXT.get('myapp/mytemplate')                         // for the app/template
                    DMP_CONTEXT.get(document.querySelector('some selector'))    // for the specified <script> tag
            */
            get: function(option) {
                var ret = DMP_CONTEXT.getAll(option);
                if (ret.length == 0) {
                    return undefined;
                }
                return ret[ret.length - 1];
            },

            /*
                Retrieves the context data for all scripts on the page matching the option.
                The returned array usually has one context item.  But when ajax retrieves the same
                template snippet multiple times, it will have multiple contexts in the array.

                    DMP_CONTEXT.getAll()                        // an array of one item: currently-executing script
                                                                // (this is the preferred way when on script's first execution)
                    DMP_CONTEXT.getAll(elem)                    // an array of one item: context for the given <script> element
                                                                // (elem retrieved with querySelector, getElementById, etc.)
                    DMP_CONTEXT.getAll('myapp/mytemplate')      // an array of all scripts matching this template name
            */
            getAll: function(option) {
                var ret = [];

                // if empty option and we have currentScript[data-context="something"], use that for the option
                if (!option && document.currentScript && document.currentScript.getAttribute('data-context')) {
                    option = document.currentScript;
                }

                // if still empty option, get the last-added context
                if (!option && DMP_CONTEXT.lastContext) {
                    ret.push(DMP_CONTEXT.lastContext.values);
                }

                // if a string, assume it is a context name in format "app/template"
                else if (typeof option === 'string' || option instanceof String) {
                    var matches = DMP_CONTEXT.contextsByName[option];
                    if (typeof matches !== "undefined") {
                        for (var m in matches) {
                            ret.push(m);
                        }
                    }
                }

                // if script[current-context="something"]
                else if (option && option.nodeType === 1 && option.nodeName.toLowerCase() == 'script' && option.getAttribute('data-context')) {
                    var c = DMP_CONTEXT.contexts[option.getAttribute('data-context')];
                    if (typeof c !== "undefined") {
                        ret.push(c.values);
                    }
                }//if

                return ret;
            },

            ////////////////////////////////////////////////////////////////////
            ///  Webpack bundling functions

            /*
                Links bundle-defined template functions so they can be calling
                from DMP_CONTEXT (i.e. outside the bundle).
            */
            loadBundle(templateFunctions) {
                var tkeys = Object.keys(templateFunctions);
                DMP_CONTEXT.log(['loading', tkeys.length, 'template functions from bundle'], tkeys);
                for (var i = 0; i < tkeys.length; i++) {
                    var tkey = tkeys[i];
                    // create an entry for this template function that knows how
                    // to import and run the dependencies (but only when asked)
                    DMP_CONTEXT.templateFunctions[tkey] = {
                        template: tkey,
                        loader: templateFunctions[tkey],
                        status: 'unresolved',
                        modules: null,
                        resolveModules: function(context) {
                            var current = this;
                            if (current.status == 'unresolved') {
                                current.status = 'resolving';
                                current.loader(function(modules) {
                                    current.modules = modules;
                                    current.status = 'resolved';
                                    DMP_CONTEXT.checkContextReady(context.id);
                                });
                            }
                        },
                        runWithContext: function(context) {
                            // call our default module functions.  some imports simply need
                            // to be loaded (e.g. css files) while others need a function to be
                            // called (e.g. js files). when a template is included more than once
                            // in a given render (e.g. <%include>), webpack doesn't "run" the import
                            // a second time, even though the js needs to run more than once.
                            var current = this;
                            if (current.modules) {
                                for (var j = 0; j < current.modules.length; j++) {
                                    var mod = current.modules[j];
                                    if (mod && mod.default && mod.default.apply) {
                                        mod.default.apply(context, [ context.values ])
                                    }
                                }
                            }
                        },
                    }
                }
            },

            /*
                Checks if the template functions related to a context are ready.
            */
            checkContextReady(contextid) {
                // get the context
                var context = DMP_CONTEXT.contexts[contextid];
                if (typeof context === "undefined") {
                    return;
                }

                // check if the functions for each template in the inheritance is loaded
                for (var i = 0; i < context.templates.length; i++) {
                    var tname = context.templates[i];
                    // is the bundle itself loaded?
                    if (typeof DMP_CONTEXT.templateFunctions[tname] === "undefined") {
                        DMP_CONTEXT.log([ context.id, '-', tname, 'not loaded [waiting]' ]);
                        // we'll just have to wait until its bundle <script> tag loads and triggers this again
                        return;
                    }
                    // has the template function run to resolve its internal dependencies?
                    if (DMP_CONTEXT.templateFunctions[tname].status != 'resolved') {
                        DMP_CONTEXT.log([ context.id, '-', tname, 'resolving internal dependencies [waiting]' ]);
                        DMP_CONTEXT.templateFunctions[tname].resolveModules(context);
                        return;
                    }
                }
                // has pendingCalls been incremented?
                if (!context.pendingCalls) {
                    DMP_CONTEXT.log([ context.id, '-', 'pendingCalls not incremented yet', '[waiting]' ]);
                    return;
                }

                // if we get here, bundles have loaded and internal dependencies are resolved
                // run the functions in order of the template inheritance
                DMP_CONTEXT.log([ context.id, '-', 'dependencies loaded and pendingCalls incremented', '[ready]' ]);
                while (context.pendingCalls > 0) {
                    context.pendingCalls--;
                    for (var j = 0; j < context.templates.length; j++) {
                        var tname = context.templates[j];
                        DMP_CONTEXT.log([ context.id, '-', 'running for', tname ]);
                        DMP_CONTEXT.templateFunctions[tname].runWithContext(context);
                    }
                }
            },

            /*
                Increments the pending call count for a context,
                then checks the bundle to see if it is loaded.
            */
            callBundleContext(contextid) {
                // get the context
                var context = DMP_CONTEXT.contexts[contextid];
                if (typeof context === "undefined") {
                    return;
                }

                // increase the trigger count and check the bundle
                context.pendingCalls++;
                DMP_CONTEXT.log([ context.id, '-', 'incrementing pendingCalls to', context.pendingCalls]);
                DMP_CONTEXT.checkContextReady(contextid);
            },

            /* Enabled when DMP's logger is set to DEBUG in settings */
            log(messages, data) {
                if (DMP_CONTEXT.logEnabled) {
                    console.debug('[DMP] ' + messages.join(' '), data || '');
                }
            },

        };//DMP_CONTEXT
    }//if

})()
