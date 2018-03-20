// note that I'm intentionally using older JS syntax to meet
// the widest possible browser base
(function() {

    if (window.DMP_CONTEXT === undefined) {

        window.DMP_CONTEXT = {

            __version__: '5.2.9',   // DMP version to check for mismatches
            contexts: {},           // contextid -> context1
            contextsByName: {},     // app/template -> [ context1, context2, ... ]
            lastContext: null,      // last inserted context (see getAll() below)
            appBundles: {},          // for the webpack provider

            /* Adds data to the DMP context under the given key */
            set: function(version, contextid, data, templates) {
                if (DMP_CONTEXT.__version__ != version) {
                    console.warn('DMP framework version is ' + version + ', while dmp-common.js is ' + DMP_CONTEXT.__version__ + '. Unexpected behavior may occur.');
                }
                // link this contextid to the data
                DMP_CONTEXT.contexts[contextid] = data;
                DMP_CONTEXT.lastContext = data
                // reverse lookups by name to contextid
                for (var i = 0; i < templates.length; i++) {
                    if (DMP_CONTEXT.contextsByName[templates[i]] === undefined) {
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
                if (!option) {
                    ret.push(DMP_CONTEXT.lastContext);
                }

                // if a string, assume it is a context name in format "app/template"
                else if (typeof option === 'string' || option instanceof String) {
                    var namemap = DMP_CONTEXT.contextsByName[option];
                    if (namemap !== undefined) {
                        for (var i = 0; i < namemap.length; i++) {
                            var c = DMP_CONTEXT.contexts[namemap[i]];
                            if (c !== undefined) {
                                ret.push(c);
                            }
                        }
                    }
                }

                // if script[current-context="something"]
                else if (option.nodeType === 1 && option.nodeName.toLowerCase() == 'script' && option.getAttribute('data-context')) {
                    var c = DMP_CONTEXT.contexts[option.getAttribute('data-context')];
                    if (c !== undefined) {
                        ret.push(c);
                    }
                }//if

                return ret;
            },

        };//DMP_CONTEXT

    }//if
})()
