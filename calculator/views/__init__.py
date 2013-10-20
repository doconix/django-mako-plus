import mako_controller


###############################################################
###   The templater for the calculator app.  I created it
###   here once and then use it throughout the views
###   within this app because we only need one.

templater = mako_controller.MakoTemplateRenderer('calculator')
