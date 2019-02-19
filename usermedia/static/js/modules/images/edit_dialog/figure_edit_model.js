import Cropper from 'cropperjs';
export const figureEditModel = () => ({
    content: [{
            title: gettext('Rotate Left'),
            type: 'action',
            tooltip: gettext('Rotate-left'),
            order: 0,
            action: editor => {
                const mediaInput = document.querySelector('#editimage .fw-media-file-input').files[0],
                    mediaPreviewer = document.querySelector('#editimage .figure-preview > div > img')
                rotateBase64Image(mediaPreviewer.src, mediaInput.type, 'left').then((response) => {
                    mediaPreviewer.src = response
                })

            },
            icon: 'redo fa-rotate-180'
        },
        {
            title: gettext('Rotate Right'),
            type: 'action',
            tooltip: gettext('Rotate-right'),
            order: 0,
            action: editor => {
                const mediaInput = document.querySelector('#editimage .fw-media-file-input').files[0],
                    mediaPreviewer = document.querySelector('#editimage .figure-preview > div > img')
                rotateBase64Image(mediaPreviewer.src, mediaInput.type, 'right').then((response) => {
                    mediaPreviewer.src = response
                })
            },

            icon: 'undo'
        },
        {
            title: gettext('Crop'),
            type: 'action',
            tooltip: gettext('Crop image'),
            order: 0,
            action: editor => {
                cropMode(true)
                const image = document.querySelector('#editimage .figure-preview > div > img')
                const cropper = new Cropper(image, {
                    viewMode: 1,
                    responsive: true,
                })
                bindEvents(cropper)
            },
            icon: 'crop'
        },
    ]
})

const bindEvents = (cropperObj) => {
    document.querySelector('.btn-select-crop').onclick = (event)=>{
        const mediaInput = document.querySelector('#editimage .fw-media-file-input').files[0],
            mediaPreviewer = document.querySelector('#editimage .figure-preview > div > img')
        mediaPreviewer.src = cropperObj.getCroppedCanvas().toDataURL(mediaInput.type)
        cropperObj.destroy()
        cropMode(false)
        document.querySelector('.btn-select-crop').onclick = null;
    }

    document.querySelector('.btn-cancel-crop').onclick = (event) => {
        console.log(event)
        cropperObj.destroy()
        cropMode(false)
        document.querySelector('.btn-cancel-crop').onclick = null;
    }
}
export const cropMode = (val) => {
    const div = document.querySelector('#editimage .figure-preview > div')
    if (val) {
        div.classList.add('crop-mode')
        document.querySelector('.btn-select-crop').classList.remove('hide')
        document.querySelector('.btn-cancel-crop').classList.remove('hide')
    } else {
        div.classList.remove('crop-mode')
        document.querySelector('.btn-select-crop').classList.add('hide')
        document.querySelector('.btn-cancel-crop').classList.add('hide')
    }
    const parentDiv = document.querySelector('#editimage').parentElement
    centerDialog(parentDiv)
}
export const centerDialog = (parentDiv) => {
    const totalWidth = window.innerWidth,
        totalHeight = window.innerHeight,
        dialogWidth = parentDiv.clientWidth,
        dialogHeight = parentDiv.clientHeight,
        scrollTopOffset = window.pageYOffset,
        scrollLeftOffset = window.pageXOffset
    parentDiv.style.top = `${(totalHeight - dialogHeight)/2 + scrollTopOffset}px`
    parentDiv.style.left = `${(totalWidth - dialogWidth)/2 + scrollLeftOffset}px`
}

export const rotateBase64Image = (base64data, type, direction) => {
    return new Promise(resolve => {
        const canvas = document.createElement("canvas")
        const ctx = canvas.getContext("2d")
        const image = new Image()
        image.src = base64data
        image.onload = () => {
            canvas.height = image.width
            canvas.width = image.height
            if (direction == 'left') {
                ctx.rotate(90 * Math.PI / 180)
                ctx.translate(0, -canvas.width)
            } else {
                ctx.rotate(-90 * Math.PI / 180);
                ctx.translate(-canvas.height, 0);
            }
            ctx.drawImage(image, 0, 0);
            resolve(canvas.toDataURL(type))
        }
    })
}