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

                DMP_CONTEXT.log([ 'created context for', context.templates[context.templates.length-1] ], context, context);
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
                // insert these functions into the main map
                Object.assign(DMP_CONTEXT.templateFunctions, templateFunctions);
                DMP_CONTEXT.log([ 'bundle functions loaded' ], null, Object.keys(templateFunctions));
                // check all contexts impacted by this bundle
                let contexts = Object.keys(templateFunctions).map(tname => DMP_CONTEXT.contextsByName[tname]);
                for (let context of flatvalid(contexts)) {
                    DMP_CONTEXT.checkContextReady(context.id);
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

                // check if the <script> tags have loaded yet
                for (var i = 0; i < context.templates.length; i++) {
                    var tname = context.templates[i];
                    // is the bundle itself loaded?
                    if (typeof DMP_CONTEXT.templateFunctions[tname] === "undefined") {
                        DMP_CONTEXT.log([ 'waiting for bundle for', tname, 'to load' ], context);
                        return;
                    }
                }
                // has pendingCalls been incremented by its <script> tag?
                if (context.pendingCalls == 0) {
                    DMP_CONTEXT.log([ 'no calls pending' ], context);
                    return;
                }

                // bundles have loaded, so run the bundle functions for the templates in this context
                // and wait for the embedded imports to load
                DMP_CONTEXT.log([ 'dependencies loaded and pendingCalls incremented' ], context);
                var importPromises = context.templates.map(tname => DMP_CONTEXT.templateFunctions[tname]());
                Promise.all(importPromises).then((modArrays) => {
                    // the embedded imports have now loaded, now run any default functions exported by them
                    while (context.pendingCalls > 0) {
                        context.pendingCalls--;
                        DMP_CONTEXT.log([ 'running bundle functions' ], context);
                        for (let mod of flatvalid(modArrays)) {
                            if (mod.default && mod.default.apply) {
                                mod.default.apply(context, [ context.values ])
                            }
                        }
                    }
                });
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
                DMP_CONTEXT.log([ 'incrementing pendingCalls to', context.pendingCalls], context);
                DMP_CONTEXT.checkContextReady(contextid);
            },

            /* Enabled when DMP's logger is set to DEBUG in settings */
            log(messages, context, data) {
                if (DMP_CONTEXT.logEnabled) {
                    if (context) {
                        messages.unshift("-");
                        messages.unshift("(" + context.templates[context.templates.length - 1] + ")");
                        messages.unshift(context.id);
                    }
                    messages.unshift('[DMP]');
                    console.debug(messages.join(' '), data || '');
                }
            },

        };//DMP_CONTEXT

        //////////////////////////////////
        ///  Helpers

        function flatvalid(arr) {
            let flattened = arr.reduce((acc, val) => acc.concat(val), []);
            return flattened.filter(val => val); // removes falsey items
        }

    }//if

})()
