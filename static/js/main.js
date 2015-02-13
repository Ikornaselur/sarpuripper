$(document).ready(function () {
    var checkState = function checkState(elm) {
        var id = elm.find('#job_id').text();
        $.get('/results/' + id, function success(data, sText, xhr) {
            var statusCode = xhr.status;
            if (statusCode === 202) {
                setTimeout(function () {
                    checkState(elm);
                }, 5000);
            }
            else if (statusCode === 200) {
                var href = elm.find('a');
                href.removeClass('disabled');
                href[0].href = data;

                elm.find('#job_status')[0].innerHTML = 'Finished';
                elm.removeClass('warning');
                elm.addClass('success');
            }
        }).fail(function error(data, sText, xhr) {
            var statusCode = xhr.status;
            if (statusCode === 500) {
                elm.find('#job_status')[0].innerHTML = 'Failed';
                elm.removeClass('warning');
                elm.addClass('danger');
            }  
        });
    };

    $('#url_form').on('submit', function (event) {
        event.preventDefault();

        var url = $('#input_url').val();

        $.post('/', {'url': url}, function (data) {
            var $resList = $('#resultList');
            var num = $resList[0].children.length;

            var itemID = 'item' + num;
            var $item = $('<tr class="warning">').appendTo($resList);

            $('<td id="job_status">processing..</th>').appendTo($item);
            $('<th id="job_id">' + data.job_id + '</th>').appendTo($item);
            $('<th id="title">' + data.file_title + '</th>').appendTo($item);
            $('<th><a href="#" class="btn btn-link disabled" style="padding: 0;">Link</a></th>').appendTo($item);

            checkState($item);
        });
    });
});
