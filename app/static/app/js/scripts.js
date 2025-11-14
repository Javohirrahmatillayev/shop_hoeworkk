/*!
* Start Bootstrap - Shop Homepage v5.0.6 (https://startbootstrap.com/template/shop-homepage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-shop-homepage/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project
const quantityInput = document.getElementById('quantity');
const priceInput = document.getElementById('price');

quantityInput.addEventListener('input', () => {
    const unitPrice = parseFloat(quantityInput.dataset.price); // data-price'dan olamiz
    const quantity = parseInt(quantityInput.value) || 0;
    priceInput.value = quantity * unitPrice;
});


