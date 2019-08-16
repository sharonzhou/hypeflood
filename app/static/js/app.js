
$(document).ready(function () {
    num_images = 500;
    $.getJSON("/static/constants.json", function(constants) {
        triplets_per_task = constants['triplets_per_task']
        $.getJSON("/static/img/images.json", function(json_images) {
            id2img = json_images['id2img']
            img2id = json_images['img2id']
            num_images = Object.keys(img2id).length
            if ('num_images' in constants) {
                num_images = constants['num_images']
            }
            ffhq_dir = '/static/img/ffhq_images/ffhqrealtwo/'
        });
    });

    $('#start_task_btn').bind('click', function(data) {
        amt_id = $('#amt_id').val()
        if (amt_id == null) {
            console.log('no amt id given');
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
        data['img'] = $('#img').val() // TODO: or .src() - see below
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
        console.log(IsJsonString(data))

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
                if (counter > triplets_per_task) {
                    // Redirect
                    $(location).attr('href', '/finish');
                } else {

                    console.log('data', data)

                    // TODO: obfuscated data['img']
                    next_img = data['img']
                    $('#img').val(next_img);
                    
                    // Switch out images
                    // TODO: S3 bucket here
                    ffhq_dir = '/static/img/ffhq_images/ffhqrealtwo/'
                    next_img_name = id2img[next_img]
                    $('#img').attr('src', ffhq_dir + next_img_name);


                    // TODO: triplets per task -> tutorial + img_per_task
                    $("#progressbar")
                        .progressbar({
                        value: counter,
                        max: triplets_per_task
                        })
                    $('#progressbar_text').html(counter)

                    // Display correctness
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
