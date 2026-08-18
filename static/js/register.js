// ── TOGGLE PASSWORD — both fields
function makeToggle(btnId, inputId) {
  const btn   = document.getElementById(btnId);
  const input = document.getElementById(inputId);
  btn.addEventListener('click', () => {
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.querySelector('.eye-icon').innerHTML = show
      ? '<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>'
      : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  });
}
makeToggle('togglePw1', 'password');
makeToggle('togglePw2', 'confirm');

// ── PASSWORD STRENGTH
const passwordInput = document.getElementById('password');
const strengthFill  = document.getElementById('strengthFill');
const strengthLabel = document.getElementById('strengthLabel');

function getStrength(val) {
  let score = 0;
  if (val.length >= 8)              score++;
  if (/[A-Z]/.test(val))           score++;
  if (/[0-9]/.test(val))           score++;
  if (/[^A-Za-z0-9]/.test(val))    score++;
  if (score <= 1) return 'weak';
  if (score <= 2) return 'fair';
  return 'strong';
}

passwordInput.addEventListener('input', () => {
  const val = passwordInput.value;
  if (!val) {
    strengthFill.className = 'strength-fill';
    strengthLabel.className = 'strength-label';
    strengthLabel.textContent = '';
    return;
  }
  const level = getStrength(val);
  const labels = { weak: 'Weak', fair: 'Fair', strong: 'Strong' };
  strengthFill.className  = `strength-fill ${level}`;
  strengthLabel.className = `strength-label ${level}`;
  strengthLabel.textContent = labels[level];
  checkMatch();
});

// ── PASSWORD MATCH
const confirmInput = document.getElementById('confirm');
const matchHint    = document.getElementById('matchHint');

function checkMatch() {
  const pw  = passwordInput.value;
  const cfm = confirmInput.value;
  if (!cfm) { matchHint.textContent = ''; matchHint.className = 'match-hint'; return; }
  if (pw === cfm) {
    matchHint.textContent = '✓ Passwords match';
    matchHint.className   = 'match-hint ok';
  } else {
    matchHint.textContent = '✗ Passwords do not match';
    matchHint.className   = 'match-hint err';
  }
}
confirmInput.addEventListener('input', checkMatch);

// ── SUBMIT — spinner + guard
document.getElementById('registerForm').addEventListener('submit', function (e) {
  if (passwordInput.value !== confirmInput.value) {
    e.preventDefault();
    matchHint.textContent = '✗ Passwords do not match';
    matchHint.className   = 'match-hint err';
    confirmInput.focus();
    return;
  }
  const btn    = document.getElementById('registerBtn');
  const text   = document.getElementById('btnText');
  const arrow  = document.getElementById('btnArrow');
  const spinner= document.getElementById('btnSpinner');
  btn.disabled         = true;
  text.textContent     = 'Creating account…';
  arrow.style.display  = 'none';
  spinner.style.display= 'inline-flex';
});


