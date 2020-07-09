// Function that makes asynchronous requests to the server (Ajax)
function processed_data() {
    $.ajax({
        type: "POST",
        url: "/start",
        data: $('form').serialize(),
        type: 'POST',
        success: function(response) {
            var json = jQuery.parseJSON(response)
            let counter = 0;
            for(key in json){
                counter++;
            }
            if (counter > 1){
                $('#question').html(json.question);
                counter = 0;
                $("input.input").val('');
                var items = jQuery("[id=answer]");
                $(items).remove();
                $('<br>', {id: 'answer'}).appendTo('#answers');
                $('<h4>', {text: 'Ответы:', id: 'answer'}).appendTo('#answers_content');
                $('<br>').appendTo('#answers_content');
                for (data in json){
                    if (counter > 0){
                        $('<span>', {class: 'answer', id: 'answer', text: counter + ')' + ' ' + json[data]}).appendTo('#answers_content');
                        $('<br>', {id: 'answer'}).appendTo('#answers_content');
                    };
                    counter++;
                };
                $('<br>').appendTo('#answers');
            }else{
                console.log('Отработал');
                $('#answers_content').remove();
                $('#form').remove();
                $('h3.quest').remove();
                $('#question').html(json.end_message);
                $('<br>').appendTo('#question');
                $('<a>', {href: '/game', id: 'start'}).appendTo('#question');
                $('<button>', {text: 'Начать сначала!'}).appendTo('#start');
            };
            console.log(response);
            },
            error: function(error) {
            console.log(error);
            }
    });
}