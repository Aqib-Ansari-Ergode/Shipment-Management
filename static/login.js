// document.getElementById('loginForm').addEventListener('submit', function (e) {
//   e.preventDefault(); // Prevent default form submission

//   const email = document.getElementById('email').value;
//   const password = document.getElementById('password').value;

//   // Send login request to the server
//   fetch('/auth/login', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({ email, password })
//   })
//   .then(response => response.json())
//   .then(data => {
//     if (data.success) {
//       alert(data.message);
//       window.location.href = '/dashboard.html'; // Redirect to protected dashboard
//     } else {
//       alert(data.message);
//     }
//   })
//   .catch(error => console.error('Error:', error));
// });
document.getElementById('loginForm').addEventListener('submit', function (e) {
  e.preventDefault(); // Prevent default form submission

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  // Get the reCAPTCHA response token
  const recaptchaToken = document.querySelector('textarea[name="g-recaptcha-response"]').value;

  // Check if reCAPTCHA is completed
  if (!recaptchaToken) {
    alert('Please complete the CAPTCHA.');
    return;
  }

  // Send login request to the server
  fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password, 'g-recaptcha-response': recaptchaToken })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert(data.message); // Optional: show a success message
      window.location.href = '/dashboard.html'; // Redirect to the dashboard route
    } else {
      alert(data.message); // Show the error message if login fails
    }
  })
  .catch(error => console.error('Error:', error));
});
