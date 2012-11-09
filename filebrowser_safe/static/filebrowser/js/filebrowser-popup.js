/* Loading this file dynamically creates a popup dialog showing the
 * media library for file selection (single file selection only at
 * this time).
 *
 * To invoke the popup, call the browseMediaLibrary function with the
 * following arguments:
 *
 *  1. Callback function: The function that will be called after the
 * popup is closed. The function will be called with a single
 * argument, which will be:
 *
 *     + null: if no selection was made (e.g. dialog closed by hitting
 * ESC), or
 *
 *     + the path of the selected file
 *
 *  2. Type of files that are selectable. Optional, defaults to image.
 *
 * The page that loads this script needs to load the following
 * resources:
 *
 *  1. css: filebrowser/css/smoothness/jquery-ui-1.9.1.custom.min.css
 *  2. js:  mezzanine/js/%s' % settings.JQUERY_FILENAME
 *  3. js:  filebrowser/js/jquery-ui-1.9.1.custom.min.js
 *  4. js:  filebrowser/js/filebrowser-popup.js (this script)
**/

$(document).ready(function() {
    gallery = $('<div id="media-library-popup"></div>');
    gallery.dialog({
        autoOpen: false,
        title: 'Media Library',
        width: 900,
    });
});

var browseMediaLibrary = function (callback, type) {
    // type defaults to image
    type = (typeof type !== 'undefined') ? type : "image";

    // the return value
    url = null;

    gallery.load("/admin/media-library/browse/?pop=4&type=" + type, function(){
        gallery.dialog('open');

        gallery.on('dialogclose', function() {
            setTimeout(function() {
                callback(url);
            });
        });

        gallery.on('click', 'a', function() {
            if($(this).hasClass('fb_selectlink')) {
                url = $(this).attr('rel');
                gallery.dialog('close');
            } else {
                gallery.load($(this).attr('href'));
            }
            return false;
        });
    });

    return true; // tell the editor that we'll take care of getting the image url
};
