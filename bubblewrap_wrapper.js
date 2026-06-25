const { spawn } = require('child_process');
const path = require('path');

const apkDir = path.join(__dirname, 'apk_build');
const cp = spawn('bubblewrap.cmd', ['build', '--manifest', '../twa-manifest.json', '--skipPwaValidation'], { cwd: apkDir, shell: true });

cp.stdout.on('data', (data) => {
    process.stdout.write(data);
    const text = data.toString();
    if (text.includes('(Y/n)')) {
        cp.stdin.write('y\n');
    } else if (text.includes('versionName for the new')) {
        cp.stdin.write('1.0.0\n');
    } else if (text.includes('Password for the Key Store')) {
        cp.stdin.write('android\n');
    } else if (text.includes('Password for the Key')) {
        cp.stdin.write('android\n');
    }
});

cp.stderr.on('data', (data) => {
    process.stderr.write(data);
});

cp.on('close', (code) => {
    process.exit(code);
});
