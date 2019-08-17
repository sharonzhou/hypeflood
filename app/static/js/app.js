
$(document).ready(function () {
    num_tutorial = 50;
    num_per_task = 100;

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
                    $(location).attr('href', '/task')
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
                if (counter > num_per_task) {
                    // Redirect
                    $(location).attr('href', '/finish');
                } else {

                    bg_div = data['bg-div']
                    $('#wrapper').css('background-image', 'url(' + bg_div + ')');

                    // Switch out images
                    next_img = data['img']
                    $('#img').attr('src', next_img);

                    $("#progressbar")
                        .progressbar({
                        value: counter,
                        max: num_per_task
                        })
                    $('#progressbar_text').html(counter)
                    
                    // Display correctness
                    $('#frac_correct').html(data['frac_correct'])
                    
                    if (data['correctness'] == '1') {
                        correctness_text = 'Correct!'
                    } else {
                        correctness_text = 'Incorrect.'
                    }

                    $('#correctness').html(correctness_text)
                    $('#correctness').fadeIn().delay(250).fadeOut();
                   
                }
            
            }

        });

    });

});
