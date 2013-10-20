Note that base.htm ends with .htm rather than .html.  While either can be rendered by Mako, the mako_controller is
programmed to only call .html files directly (i.e. without an explicit view).

Therefore, since this ends with .htm instead, it can only be used as a template ancestor.  If the browser tried
to go to /base/base/, it would get a 404 not found error.  In other words, .htm files can't be called by the browser.