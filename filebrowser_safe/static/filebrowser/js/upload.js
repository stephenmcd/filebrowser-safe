(function($, global){
    var queue = [];

    // would be nicer to return at the top, but some browsers complain about "unreachable" code
    if(!global.FormData){
        console.log('XHR file uploads are not supported. Falling back to regular uploads.');

        // replace the fancy input wrapper with a standard file input
        $(function(){
            $('#upload-form').find('.file-input-wrapper').replaceWith('<input name="Filedata" type="file" />');
        });
    }else{
        $(function(){
            var form = $('#upload-form');
            var formData = form.data();
            var doneRedirect = formData.redirectWhenDone || '/';
            var extensions = formData.allowedExtensions && formData.allowedExtensions.split(',');
            var allowedSize = formData.sizeLimit && parseInt(formData.sizeLimit);

            form.on('change', 'input[type="file"]', function(e){
                var input = this;
                var selectedFile = input.files[0];
                var el = $(input).closest('.file-input-wrapper');
                var status = el.find('.status');
                var hasExtensionError = !validateExtension(selectedFile, extensions);
                var hasSizeError = !validateSize(selectedFile, allowedSize);

                // shows the error message if there was an error
                if(hasExtensionError || hasSizeError){
                    el.addClass('selected');

                    status
                        .addClass('error')
                        .text(hasSizeError ? formData.sizeError : formData.extensionError);

                }else if(input.value && selectedFile){
                    // jquery has .clone, however it has some strange behavior,
                    // like assigning id="null" to the newly-created element.
                    // maybe it's fixed in newer version but grapelli seems to be on 1.7
                    if(!el.next().is('.file-input-wrapper')){
                        el.after(el[0].outerHTML);
                        el.addClass('selected');
                    }

                    // display the selected file's name
                    status
                        .removeClass('error')
                        .text(selectedFile.name);
                }
            });

            form.on('submit', function(e){
                e.preventDefault();
                var data = form.serializeArray();
                var url = form.attr('action');

                // hide the "clear queue" button, we don't
                // support cancelling of uploads yet
                $('a.deletelink').hide();

                // go through all of the inputs and add them to the queue
                $.each($('.file-input-wrapper'), function(index, el){
                    var element = $(el);
                    var input = element.find('input[type="file"]').eq(0)[0];

                    // only add it to the queue if it has a selected file
                    if(input && input.files.length){
                        var promise = queueFile(url, data, {
                            field: input.name,
                            value: input.files[0]
                        });

                        var progress = element.find('.progress-inner');

                        element.addClass('in-progress');

                        // when failed, show the error message
                        promise.fail(function(){
                            element.find('.status').addClass('error').text(formData.serverError);
                        });

                        // on progress, update the progressbar
                        promise.progress(function(current){
                            var inPercent = current + '%';
                            progress.css('width', inPercent);
                            progress.attr('data-percentage', inPercent);
                        });

                        // this one should be at the bottom so it always fires last.
                        // in any case the upload should be marked as being "done"
                        promise.always(function(){
                            element.removeClass('in-progress selected').addClass('done');

                            // note that the file input needs to be cleared so pressing
                            // "upload" doesn't trigger another upload
                            input.value = '';

                            // redirect if there's nothing left in the queue
                            if(queue.length === 0){
                                window.location.href = doneRedirect;
                            }
                        });
                    }
                });

                // if the queue is empty, redirect immediately
                if(queue.length === 0){
                    window.location.href = doneRedirect;
                }
            });

            // clears a particular item that has been selected
            form.on('click', '.cancel-button', function(){
                var element = $(this).closest('.file-input-wrapper');

                if(element.siblings('.file-input-wrapper').length){
                    element.remove();
                }else{
                    element
                        .removeClass('selected in-progress')
                        .find('input[type="file"]').eq(0)[0].value = '';
                }
            });

            // clears all of the selected uploads
            $('a.deletelink').click(function(e){
                e.preventDefault();

                var wrappers = form.find('.file-input-wrapper');

                $.each(wrappers, function(index, current){
                    var wrapped = $(current);

                    if(index + 1 === wrappers.length){
                        wrapped.find('input[type="file"]').eq(0)[0].value = '';
                        wrapped.removeClass('selected in-progress done');
                    }else{
                        wrapped.remove();
                    }
                });
            });
        });
    }

    function queueFile(url, data, file){
        var xhr = new global.XMLHttpRequest();
        var formData = new global.FormData();
        var deferred = $.Deferred();
        var sendRequest = function(){
            xhr.open('POST', url, true);
            xhr.send(formData);
        };

        // add a reference to the xhr object just in case
        // it isn't used atm but might be useful for something
        // like aborting a request that is in progress
        deferred.xhr = xhr;

        // add all of the hidden fields to the request
        $.each(data, function(index, item){
            formData.append(item.name, item.value);
        });

        // add the file to the request
        formData.append(file.field, file.value);

        xhr.addEventListener('readystatechange', function(){
            var status = xhr.status;
            var index = queue.indexOf(deferred);

            // anything different from 4 means "not-ready"
            if(xhr.readyState !== 4) return;

            // remove the deferred from the queue
            if(index > -1){
                queue.splice(index, 1);
            }

            // upload was successful
            if(status > 0 && 200 <= status && status < 300){
                deferred.notify(100);
                deferred.resolve(xhr.responseText);
            // upload failed
            }else{
                deferred.reject(status);
            }
        });

        // bear in mind that its xhr.upload, not xhr
        xhr.upload.addEventListener('progress', function(event){
            if(event.lengthComputable){
                deferred.notify((event.loaded/event.total*100).toFixed(2));
            }
        });

        // if there are other pending uploads, wait for the
        // last one to finish before starting the upload
        if(queue.length){
            queue[queue.length - 1].always(sendRequest);
        // otherwise just start
        }else{
            sendRequest();
        }

        queue.push(deferred);
        return deferred;
    }

    // checks whether the specified file's extension is allowed
    function validateExtension(file, extensions){
        if(extensions){
            var fileExtension = file.name.slice(file.name.lastIndexOf('.'), file.name.length);

            if(extensions.indexOf(fileExtension) === -1){
                return false;
            }
        }

        return true;
    }

    // checks whether a file's size is under the limit
    function validateSize(file, allowed){
        if(allowed){
            if(typeof allowed === 'number' && !global.isNaN(allowed)){
                return file.size <= allowed;
            }

            return false;
        }

        return true;
    }

})(jQuery, window);
