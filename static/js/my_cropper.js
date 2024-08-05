document.addEventListener('DOMContentLoaded', function() {
    const image = document.getElementById('image');
    const saveChangesButton = document.getElementById('save-changes');
    const croppedImageInput = document.getElementById('cropped_image');
    const filterSelect = document.getElementById('filter');

    let cropper;

    image.onload = function() {
        cropper = new Cropper(image, {
            aspectRatio: NaN,
            viewMode: 1,
            autoCropArea: 1,
            responsive: true,
            crop(event) { },
        });
    };

    saveChangesButton.addEventListener('click', function() {
        const data = cropper.getData();
        document.getElementById('id_crop_x').value = Math.round(data.x); 
        document.getElementById('id_crop_y').value = Math.round(data.y);
        document.getElementById('id_crop_width').value = Math.round(data.width);
        document.getElementById('id_crop_height').value = Math.round(data.height);
    });
});