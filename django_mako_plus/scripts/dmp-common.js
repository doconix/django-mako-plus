(function() {    
    if (window.DMP_CONTEXT === undefined) {
        window["DMP_CONTEXT"] = {
            /* Check for the dmp version so we don't have mismatches */
            __version__: '4.3.2',
            
            /* Adds data to the DMP context under the given key */
            setContext: function(version, contextid, data) {
                if (DMP_CONTEXT.__version__ != version) {
                    console.warn('DMP framework version is ' + version + ' dmp-common.js is ' + DMP_CONTEXT.__version__ + '. Unexpected behavior may occur.');
                }
                DMP_CONTEXT[contextid] = data;
            },//addContext

            /* Adds a <script> element dynamically, which ensures the fetched script has document.currentScript (see docs) */
            addScript: function(uid, contextid, src, async) {
                var n = document.createElement("script");
                n.id = uid;
                n.async = async;
                n.setAttribute("data-context", contextid);
                n.src = src;
                // try to add immediately after this script's tag, with fallback to <head>
                if (document.currentScript) {
                    document.currentScript.parentNode.insertBefore(n, document.currentScript.nextSibling);
                }else{
                    document.head.appendChild(n);
                }
            },//addScript

        };//DMP_CONTEXT
    }//if
})()