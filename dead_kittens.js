	// class Beta {
	// 	constructor() {
	// 		// Initialize random alpha, beta
	// 		this.alpha = 1;
	// 		this.beta = 1;
	// 	}

	// 	sample() {
	// 		return testbeta(self.alpha, self.beta, 1);
	// 	};
	// }


		 		// Update Beta distributions
	 		// if (img_selected == img1) {
	 		// 	betas[root_img, img1].alpha += 1
	 		// 	betas[root_img, img2].beta += 1
	 		// } else {
	 		// 	betas[root_img, img2].alpha += 1
	 		// 	betas[root_img, img1].beta += 1
	 		// }

	 		// TODO: every n=1+ iterations, async save to db

	 		// Sample next triplet (next root img randomly and best two possible pairs)
	 		// Send this to python
	 		// console.log('hellooooo about to send post')

// $.get("/compute", function(data) {
			// 	console.log('returned to js')
			//     console.log($.parseJSON(data))
			// })

	 		// next_root_img = Math.floor(Math.random() * num_images);
	 		// next_pair_img = betas[root_img];
	 		// max1 = -Infinity;
	 		// max2 = -Infinity;
	 		// for (var img in next_pair_img) {
	 		// 	beta = next_pair_img[img]
	 		// 	console.log(beta)
	 		// 	// Get best two samples
	 		// 	sample = beta.sample();
	 		// 	console.log('Sample:', sample)
	 		// 	if (sample > max1) {
	 		// 		max2 = max1;
	 		// 		max1 = sample;
	 		// 	} else if (sample > max2) {
	 		// 		max2 = sample;
	 		// 	}
	 		// }

	 		// // Switch out images
	 		// next_img1 = max1
	 		// next_img2 = max2

	 		// $('#img1') = next_img1 + '.png'
	 		// $('#img2') = next_img2 + '.png'

	 		// $('input[name=r]').val(next_root_img)
	 		// $('input[name=c1]').val(next_img1)
	 		// $('input[name=c2]').val(next_img2)

	 		// $('#img1_select]').val(next_img1)
	 		// $('#img2_select]').val(next_img2)