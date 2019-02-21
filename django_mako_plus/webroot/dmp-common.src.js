if (!window["DMP_CONTEXT"]) {

    /** Main DMP class - a single instance of this class is set as window.DMP_CONTEXT */
    class DMP {
        constructor() {
            this.__version__ = '5.10.10';    // DMP version to check for mismatches
            this.contexts = {};             // id -> context1
            this.templates = {};            // app/template -> info
            this.lastContext = null;        // last inserted context (see getAll() below)
            this.logEnabled = null;         // whether the log is DEBUG in settings
        }

        /*
            Sets a context in the main object.
            This is called by the DMP context provider.
        */
        set(context) {
            this.logEnabled = context.log || this.logEnabled;
            if (this.__version__ != context.version) {
                this.log(['server version', context.version, 'is different from dmp-common.js', DMP_CONTEXT.__version__, '- unexpected behavior may occur']);
            }
            this.log([ 'creating context for', context.templates[context.templates.length-1] ], context, context);
            this.contexts[context.id] = context;
            this.lastContext = context;
            for (let tname of context.templates) {
                this.getTemplate(tname).addContext(context);
            }
        }

        /* Gets the template object for the given name, creating if needed */
        getTemplate(tname) {
            let template = this.templates[tname]
            if (!template) {
                template = new Template(this, tname);
                this.templates[tname] = template;
            }
            return template;
        }

        /* Ensures a context: gets the context by the given id, or returns the context if not a string */
        getContextById(context) {
            if (typeof context === 'string' || context instanceof String) {
                return this.contexts[context];
            }
            return context;  // might already be a context object
        }

        /*
            Convenience method to retrieve context values. If multiple script contexts are found,
            such as when ajax retrieves the same template snippet multiple times, the last one is
            returned. This method does not return the full context objects but rather the values dictionary.

                DMP_CONTEXT.get()                                           // values for the currently-executing script
                DMP_CONTEXT.get('myapp/mytemplate')                         // values for the app/template
                DMP_CONTEXT.get(document.querySelector('some selector'))    // values for the specified <script> tag
                DMP_CONTEXT.get('context id')                               // values for the given context
        */
        get(option) {
            let contexts = this.getAll(option);
            if (contexts.length == 0) {
                return undefined;
            }
            return contexts[contexts.length - 1].values;
        }

        /*
            Retrieves the contexts for all scripts on the page matching the option.
            The returned array usually has one context item, but if a template is included
            more than once in a request, it will generally have a context for each render.
            Note that this method returns the full context objects, not just the values.
            Ways to call:
                // returns an array of one: the currently-executing script
                // (this is the preferred way when on script's first execution)
                DMP_CONTEXT.getAll()
                // returns an array of one: the context for the given <script> element
                // (elem retrieved with querySelector, getElementById, etc.)
                DMP_CONTEXT.getAll(script_elem)
                // an array of all contexts matching this template name
                DMP_CONTEXT.getAll('myapp/mytemplate')
                // an array of one: the context matching the given id
                DMP_CONTEXT.getAll('context id')
        */
        getAll(option) {
            // if empty option and we have currentScript[data-context="something"], use that for the option
            if (!option && document.currentScript && document.currentScript.getAttribute('data-context')) {
                option = document.currentScript;
            }
            // if still empty option, get the last-added context
            if (!option && this.lastContext) {
                return [ this.lastContext ];
            }
            // if a string, assume it is a context name in format "app/template"
            else if (typeof option === 'string' || option instanceof String) {
                let template = this.templates[option];
                if (template) {
                    return template.contexts;
                }
                let context = this.getContextById(option);
                if (context) {
                    return [ context ]
                }
            }
            // if script[current-context="something"]
            else if (option && option.nodeType === 1 && option.nodeName.toLowerCase() == 'script' && option.getAttribute('data-context')) {
                let context = this.getContextById(option.getAttribute('data-context'));
                if (context) {
                    return [ context ]
                }
            }//if
            return [];
        }


        ////////////////////////////////////////
        ///  Webpack-related methods

        /*
            Links bundle-defined template functions so they can be calling
            from DMP_CONTEXT (i.e. outside the bundle).
        */
        loadBundle(bundle) {
            // insert these functions into the main map
            this.log([ 'initializing loaders in bundle' ], null, Object.keys(bundle));
            for (let tname of Object.keys(bundle)) {
                let template = this.getTemplate(tname);
                template.loader = bundle[tname];
            }
            // check the templates impacted by this bundle
            for (let tname of Object.keys(bundle)) {
                this.getTemplate(tname)._checkReady();
            }
        }

        /* Called by the webpack provider - main trigger for template code */
        callBundleContext(context) {
            context = this.getContextById(context);
            // wait for the template functions to load from the bundle
            let notifyPromises = context.templates.map(tname => this.getTemplate(tname).notifyReady());
            Promise.all(notifyPromises).then(templates => {
                for (let template of templates) {
                    this.log([ 'calling', template.tname ], context, context);
                    template.call(context);
                }
            });
        }

        /* Enabled when DMP's logger is set to DEBUG in settings */
        log(messages, context, data) {
            if (this.logEnabled) {
                context = this.getContextById(context);
                if (context) {
                    messages.unshift("-");
                    messages.unshift("(" + context.templates[context.templates.length - 1] + ")");
                    messages.unshift(context.id);
                }
                messages.unshift('[DMP]');
                console.debug(messages.join(' '), data || '');
            }
        }

    }//DMP class


    class Template {
        constructor(dmp, tname) {
            this.dmp = dmp;                 // backwards reference to DMP instance
            this.tname = tname;             // app/page name of this template
            this.contexts = [];             // contexts that include this template
            this.loader = null;             // webpack function associated with this template
            this.loaderCalled = false;      // whether the loader function has been called
            this.modules = null;            // the dynamically-imported modules (once loaded)
            this.unresolvedPromises = [];   // promise queue during loading of webpack function
        }

        /* Associates a context with this template */
        addContext(context) {
            this.contexts.push(context);
        }

        /*
            Calls the default exported functions in the modules list of this template.
            Assumes that the modules are loaded (notifyReady has resolved).
        */
        call(context) {
            context = this.dmp.getContextById(context);
            if (context) {
                // step through the imported modules and run any that have a default function.
                // some modules take effect simply by importing them (e.g. CSS), but other
                // modules export a function that needs to be called (e.g. JS). The function is
                // required because importing only runs the first time it's imported. If a template
                // is included more than once in a request (such as <%include> in a for loop), the
                // JS should run once for each time it's included. Hence a default exported function.
                for (let module of this.modules) {
                    if (module && module.default && module.default.apply) {
                        module.default.apply(context, [ context.values ]);
                    }
                }
            }
        }

        /* Returns a promise to be resolved when the bundle for this template is loaded */
        notifyReady() {
            let promise = new Promise((resolve, reject) => {
                this.unresolvedPromises.push(resolve);
            });
            this._checkReady();
            return promise;
        }

        /*
            Private method that checks loading status, resolving promises if ready.
            This is triggered internally each time the template might be ready:
                1. loadBundle() is called by the __entry__ file
                2. the dynamic imports finish loading
                3. callBundleContext calls notifyReady (might be ready immediately)
        */
        _checkReady() {
            // is the bundle here yet?
            if (!this.loader) {
                this.dmp.log([ this.tname, 'waiting for bundle' ]);
                return;
            }
            // not all templates in a bundle need to load, so only
            // continue if someone has asked to be notified
            if (this.unresolvedPromises.length == 0) {
                return;
            }
            // has the loader function run yet?
            if (!this.loaderCalled) {
                this.dmp.log([ this.tname, 'calling loader' ]);
                this.loaderCalled = true;
                Promise.all(this.loader()).then((modules) => {
                    this.modules = modules;
                    this._checkReady();
                });
                return;
            }
            // are we still waiting on the dynamically-imported modules to load?
            if (this.modules == null) {
                this.dmp.log([ this.tname, 'waiting on dynamic imports' ]);
                return;
            }
            // stick a fork in this template...it's ready - notify everyone
            while (this.unresolvedPromises.length > 0) {
                this.dmp.log([ this.tname, 'dynamic imports loaded' ]);
                let resolve = this.unresolvedPromises.shift();
                resolve(this);
            }
        }
    }

    // main instance - right now it has to be in the global window scope
    // so <script> tags can get to it.
    // we checked at the top, but checking for rerun of this script one
    // more time before setting in the window
    if (!window["DMP_CONTEXT"]) {
        window["DMP_CONTEXT"] = new DMP();
    }
}

// default export for ES6 environments
export default window["DMP_CONTEXT"];
