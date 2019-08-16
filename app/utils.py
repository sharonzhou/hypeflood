

def get_images_from_id(img_triplet_id):
    images['img_triplet_id'] = img_triplet_id
    images['root_img'] = x
    images['img1'] = x
    images['img2'] = y
    return images

def update_beta_dists(images, img_selected):
    row = images['root_img']
    if img_selected == images['img1']:
        # Update img1 as selected and img2 as not selected
        pass
    else:
        # Update vice versa
        pass
    return

def sample_next_triplet(root_img):
    next_root_img = root_img + 1
    # two highest images
    return img_triplet_id
