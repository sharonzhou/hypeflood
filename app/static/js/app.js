var idle_time = 0;
$(document).ready(function () {
    
    $.getJSON("/static/constants.json", function(constants) {
        num_tutorial = constants['num_tutorial']
        num_per_task = constants['num_per_task']
        num_images = constants['num_images']
        tutorial_pass_acc = constants['tutorial_pass_acc']
    })

    $('#start_task_btn').bind('click', function(data) {
        amt_id = $('#amt_id').val()
        if (amt_id == null) {
            console.log('No AMT id given.');
        } else {
            data = {}
            console.log(amt_id);
            data['amt_id'] = amt_id;
            data = JSON.stringify(data)
			$.ajax({
	            type: "POST",
	            processData: false,
	            contentType: false,
	            cache: false,
	            data: data,
	            url: '/login',
	            success: function (response) {
                    response = $.parseJSON(response);
                    data = response["data"];
                    console.log(data);
                    $(location).attr('href', data['url_']);
                }
            });
        }
    }); 

    $("#submit-btn").click(function() {
        selected_radio = $('input[name=selected]:checked')
        selected = selected_radio.val()
        if (selected == null) {
            console.log('Nothing selected.');
            return
        } else {
           selected_radio.prop('checked', false); 
        }

        data = {}
        data['img'] = $('#img').attr('src') 
        data['bg-div'] = $('#wrapper').css('background-image')
        data['selected'] = selected 
        data['counter'] = $('#counter').val() + 1
        
        function IsJsonString(str) {
            try {
                JSON.parse(str);
            } catch (e) {
                return false;
            }
            return true;
        }
        data = JSON.stringify(data)

        $.ajax({
            type: "POST",
            processData: false,
            contentType: false,
            cache: false,
            data: data,
            url: '/feedback',
            success: function (response) {
                response = $.parseJSON(response);
                data = response['data'];

                counter = data['counter']
                frac_correct = data['frac_correct']
                is_spammer = data['spammer']
                if ((counter >= num_per_task) || (counter == num_tutorial && frac_correct < tutorial_pass_acc) || is_spammer) {

                    // Redirect
                    $(location).attr('href', '/finish');
                } else {

                    bg_div = data['bg-div']
                    $('#wrapper').css('background-image', 'url(' + bg_div + ')');


                    // Switch out images
                    next_img = data['img']
                    $('#img').attr('src', next_img);


                    // Update progress bar
                    $("#progressbar")
                        .progressbar({
                        value: counter,
                        max: num_per_task
                        })
                    $('#progressbar-text').html(counter)
                    

                    // Display correctness
                    $('#frac-correct').html(frac_correct)
                    
                    if (data['correctness'] == '1') {
                        correctness_text = 'Correct!'
                    } else {
                        correctness_text = 'Incorrect'
                    }

                    $('#correctness').html(correctness_text)
                    $('#correctness').fadeIn().delay(250).fadeOut();
                   
                }
            
            }

        });

    });

    // Increment the idle time counter every minute.
    var idle_interval = setInterval(timerIncrement, 1000); // 1 sec

    // Zero the idle timer on mouse movement.
    $(this).mousemove(function (e) {
        idle_time = 0;
    });

    $(this).keypress(function (e) {
        idle_time = 0;
    });

    function timerIncrement() {
        idle_time = idle_time + 1;
        if (idle_time > 8) { // 8 sec
            // Redirect, if not already redirected or at end task screen
            if ((window.location.href.indexOf("idle") == -1) && (window.location.href.indexOf("finish") == -1)) {
                $(location).attr('href', '/idle');
            }
        }
    }

});
