# from utils import get_images_from_id, update_beta_dists, sample_next_triplet
# @app.route("/task", methods=['POST'])
# # r=<int:root_img>&c1=<int:img1>&c2=<int:img2>&s=<int:img_selected>")
# # def next_img(root_img, img1, img2, img_selected):
# def next_img():
#     """Gives next image based on posteriors
#     """
#     if request.method == 'POST':
#         root_img = request.form['r']
#         img1 = request.form['c1']
#         img2 = request.form['c2']
#         img_selected = request.form['s']
#         images = { 'root_img': root_img,
#                     'img1': img1,
#                     'img2': img2,
#                     'img_selected': img_selected,
#                  }
#         print(images)
#         print('python')
#         # send dict to another url that JS catches
#         return render_template("index.html", images=images)

# @app.route("/submit", methods=['POST'])
# def submit():
#     if request.method == 'POST':
#         root_img = request.form['root_img']
#         img1 = request.form['img1']
#         img2 = request.form['img2']
#         img_selected = request.form['img_selected']
#         # Get triplet and update Beta dists conditioned on root_img
#         if img_select == img1:
#             beta_selected =
#             beta_unselected = 
#         else:
#             beta_selected = 
#             beta_unselected = 
#         update_beta_dists(images, img_selected)

#         # Greedily select next triplet and return id
#         sample_next_triplet(root_img)
#         return redirect(url_for('next_img', img_triplet_id=img_triplet_id))


