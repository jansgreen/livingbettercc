const myModal = document.getElementById('myModal');
const myInput = document.getElementById('myInput');

if (myModal && myInput) {
  myModal.addEventListener('shown.bs.modal', () => {
    myInput.focus();
  });
}

document.addEventListener('DOMContentLoaded', function () {
  try {
    const cloudImgs = document.querySelectorAll('img[src*="res.cloudinary.com"]');
    cloudImgs.forEach((img) => {
      // Remove problematic class
      if (img.classList.contains('object-fit-cover')) {
        img.classList.remove('object-fit-cover');
      }

      // Force visibility-friendly inline styles
      img.style.width = '100%';
      img.style.height = 'auto';
      img.style.display = 'block';

      const parent = img.parentElement;
      if (parent) {
        const inlineStyle = (parent.getAttribute('style') || '').toLowerCase();

        // Fix collapsed height
        const heightIsZero = inlineStyle.includes('height:0') || parent.style.height === '0px' || parent.style.height === '0';
        if (heightIsZero) {
          parent.style.minHeight = '1px';
          parent.style.height = '';
        }

        // Fix overflow hidden
        const overflowHidden = inlineStyle.includes('overflow:hidden') || parent.style.overflow === 'hidden';
        if (overflowHidden) {
          parent.style.overflow = 'visible';
        }

        // Fix flex collapsed containers (only if set inline)
        const displayFlexInline = inlineStyle.includes('display:flex') || parent.style.display === 'flex';
        if (displayFlexInline) {
          parent.style.display = 'block';
        }

        // Fix accidental opacity:0
        const opacityZero = inlineStyle.includes('opacity:0') || parent.style.opacity === '0';
        if (opacityZero) {
          parent.style.opacity = '1';
        }
      }
    });
  } catch (e) {
    // Silently ignore to avoid breaking pages
    console && console.warn && console.warn('Cloudinary image fix error:', e);
  }
});
