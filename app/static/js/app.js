
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
    
    
	$('.image_select').bind("click", function(data) {
	 	root_img = $('#root_img').attr('value')
	 	img1 = $('#img1').val()
	 	img2 = $('#img2').val()
	 	img_selected = $(this).val();
	 	
        if (img_selected == null) {
	 		console.log('no image selected')
	 	} else {

	 		data = {}
	 		data['root_img'] = root_img
	 		data['img1'] = img1
	 		data['img2'] = img2
	 		data['img_selected'] = img_selected
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
	            url: '/compute',
	            success: function (response) {
	                response = $.parseJSON(response);
        	 		data = response['data'];

                    counter = data['counter']
                    if (counter > triplets_per_task) {
                        // Redirect
                        $(location).attr('href', '/finish');
                    } else {

                        next_root_img = data['root_img']
                        next_img1 = data['img1']
                        next_img2 = data['img2']

                        $('#root_img').attr('value', next_root_img);
                        $('#img1').val(next_img1);
                        $('#img2').val(next_img2);
                        
                        // Switch out images
                        ffhq_dir = '/static/img/ffhq_images/ffhqrealtwo/'
                        next_root_img_name = id2img[next_root_img]
                        next_img1_name = id2img[next_img1]
                        next_img2_name = id2img[next_img2]
                        $('#root_img').attr('src', ffhq_dir + next_root_img_name);
                        $('#img1').attr('src', ffhq_dir + next_img1_name);
                        $('#img2').attr('src', ffhq_dir + next_img2_name);

                        $("#progressbar")
                            .progressbar({
                            value: counter,
                            max: triplets_per_task
                            })
                        $('#progressbar_text').html(counter)
                    }
	            }
	        });


	 	}

	});
});
