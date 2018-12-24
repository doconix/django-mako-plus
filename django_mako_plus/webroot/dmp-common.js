// note that I'm intentionally using older JS syntax to meet
// the widest possible browser base
(function() {

    // if dmp-common.js already ran (duplicate <script> or inclusion in two bundles),
    // short circuit because it may already have data in it.
    if (window.DMP_CONTEXT) {
        return;
    }

    // connect the dmp object
    window.DMP_CONTEXT = {
        __version__: '5.7.7',   // DMP version to check for mismatches
        contexts: {},           // contextid -> context1
        contextsByName: {},     // app/template -> [ context1, context2, ... ]
        lastContext: null,      // last inserted context (see getAll() below)
        bundleFunctions: {},    // functions that wraps template JS/CSS (see DMP's webpack docs)

        /* Adds data to the DMP context under the given key */
        set: function(version, contextid, data, templates) {
            if (DMP_CONTEXT.__version__ != version) {
                console.warn('DMP framework version is ' + version + ', while dmp-common.js is ' + DMP_CONTEXT.__version__ + '. Unexpected behavior may occur.');
            }
            // link this contextid to the data and templates
            DMP_CONTEXT.contexts[contextid] = {
                id: contextid,
                data: data,
                templates: templates,
                triggerCount: 0
            };
            DMP_CONTEXT.lastContext = DMP_CONTEXT.contexts[contextid];
            // reverse lookups by name to contextid
            for (var i = 0; i < templates.length; i++) {
                if (typeof DMP_CONTEXT.contextsByName[templates[i]] === "undefined") {
                    DMP_CONTEXT.contextsByName[templates[i]] = [];
                }
                DMP_CONTEXT.contextsByName[templates[i]].push(contextid);
            }
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
                ret.push(DMP_CONTEXT.lastContext.data);
            }

            // if a string, assume it is a context name in format "app/template"
            else if (typeof option === 'string' || option instanceof String) {
                var namemap = DMP_CONTEXT.contextsByName[option];
                if (typeof namemap !== "undefined") {
                    for (var i = 0; i < namemap.length; i++) {
                        var c = DMP_CONTEXT.contexts[namemap[i]];
                        if (typeof c !== "undefined") {
                            ret.push(c.data);
                        }
                    }
                }
            }

            // if script[current-context="something"]
            else if (option.nodeType === 1 && option.nodeName.toLowerCase() == 'script' && option.getAttribute('data-context')) {
                var c = DMP_CONTEXT.contexts[option.getAttribute('data-context')];
                if (typeof c !== "undefined") {
                    ret.push(c.data);
                }
            }//if

            return ret;
        },


        ////////////////////////////////////////////////////////////////////
        ///  Webpack bundling functions

        /*
            Links a bundle-defined template function so it can be called
            from DMP_CONTEXT (i.e. outside the bundle). We only allow functions
            to link once so state isn't overwritten by duplicate script tags.
        */
        linkBundleFunction(template, func) {
            if (typeof DMP_CONTEXT.bundleFunctions[template] === "undefined") {
                DMP_CONTEXT.bundleFunctions[template] = func;
            }
        },

        /*
            Checks if bundle-defined template functions need to run for a function.
            We check with every script's onLoad as well as an explicit call. This
            ensures the functions are run when async and/or out of order.
        */
        checkBundleLoaded(contextid) {
            // get the context
            var context = DMP_CONTEXT.contexts[contextid];
            if (typeof context === "undefined") {
                return;
            }

            // are all the bundles we need loaded?
            for (var i = 0; i < context.templates.length; i++) {
                var template = context.templates[i];
                if (typeof DMP_CONTEXT.bundleFunctions[template] === "undefined") {
                    return;
                }
            }

            // everything is here, so run the bundle functions
            // for each time the triggerBundleContext() was called
            while (context.triggerCount > 0) {
                context.triggerCount--;
                for (var i = 0; i < context.templates.length; i++) {
                    var template = context.templates[i];
                    if (DMP_CONTEXT.bundleFunctions[template]) {    // might be null (if no scripts for the template)
                        DMP_CONTEXT.bundleFunctions[template]();
                    }
                }
            }
        },

        /*
            Triggers a template context to run a given bundle.
        */
        triggerBundleContext(contextid) {
            // get the context
            var context = DMP_CONTEXT.contexts[contextid];
            if (typeof context === "undefined") {
                return;
            }

            // increase the trigger count and check the bundle
            context.triggerCount++;
            DMP_CONTEXT.checkBundleLoaded(contextid);
        }

    };//DMP_CONTEXT

})()
