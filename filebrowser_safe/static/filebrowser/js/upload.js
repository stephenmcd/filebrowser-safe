(function($, global){
    var queue = [];

    // would be nicer to return at the top, but some browsers complain about "unreachable" code
    if(!global.FormData){
        console.log('XHR file uploads are not supported. Falling back to regular uploads.');

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

                el.find('span').hide();

                if(!validateExtension(selectedFile, extensions)){
                    input.value = '';
                    el.find('span.error.extension-error').show();
                }else if(!validateSize(selectedFile, allowedSize)){
                    input.value = '';
                    el.find('span.error.size-error').show();
                }else if(input.value && selectedFile){
                    // jquery has .clone, however it has some strange behavior,
                    // like assigning id="null" to the newly-created element
                    if(!el.next().is('.file-input-wrapper')){
                        el.after(el[0].outerHTML);
                    }

                    el.find('.filename').show().text(selectedFile.name);
                }
            });

            form.on('submit', function(e){
                e.preventDefault();
                var data = form.serializeArray();
                var url = form.attr('action');

                $('a.deletelink').hide();

                $.each($('.file-input-wrapper'), function(index, el){
                    var element = $(el);
                    var input = element.find('input[type="file"]').eq(0)[0];

                    if(input && input.files.length){
                        var promise = queueFile(url, data, {
                            field: input.name,
                            value: input.files[0]
                        });

                        var progress = element.find('.progress').css('display', 'inline-block').find('.progress-inner');
                        element.find('label').hide();

                        promise.fail(function(){
                            element.find('span').hide();
                            element.find('span.error.server-error').show();
                        });

                        promise.progress(function(current){
                            var inPercent = current + '%';
                            progress.css('width', inPercent);
                            progress.attr('data-percentage', inPercent);
                        });

                        // this one should be at the bottom so
                        // it always fires last
                        promise.always(function(){
                            if(queue.length === 0){
                                window.location.href = doneRedirect;
                            }
                        });
                    }
                });

                if(queue.length === 0){
                    window.location.href = doneRedirect;
                }
            });

            $('a.deletelink').click(function(e){
                e.preventDefault();

                var wrappers = form.find('.file-input-wrapper');

                $.each(wrappers, function(index, current){
                    var wrapped = $(current);

                    if(index + 1 === wrappers.length){
                        wrapped.find('input[type="file"]')[0].value = '';
                        wrapped.find('span, .progress').hide();
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

        deferred.xhr = xhr;

        $.each(data, function(index, item){
            formData.append(item.name, item.value);
        });

        formData.append(file.field, file.value);

        xhr.addEventListener('readystatechange', function(){
            var status = xhr.status;
            var index = queue.indexOf(deferred);

            if(xhr.readyState !== 4) return;

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

        if(queue.length){
            queue[queue.length - 1].always(sendRequest);
        }else{
            sendRequest();
        }

        queue.push(deferred);
        return deferred;
    }

    function validateExtension(file, extensions){
        if(extensions){
            var fileExtension = file.name.slice(file.name.lastIndexOf('.'), file.name.length);

            if(extensions.indexOf(fileExtension) === -1){
                return false;
            }
        }

        return true;
    }

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
