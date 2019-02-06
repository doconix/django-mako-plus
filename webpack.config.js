const path = require('path');


module.exports = (env, argv) => {
    let DEBUG = argv.mode != 'production';
    return {
        entry: [
            './django_mako_plus/webroot/dmp-common.src.js',
        ],
        output: {
            path: path.resolve(__dirname),
            filename: DEBUG ? './django_mako_plus/webroot/dmp-common.js' : './django_mako_plus/webroot/dmp-common.min.js',
        },
        module: {
            rules: [
                {
                    test: /\.js$/,
                    use: 'babel-loader',
                },
            ],
        },
        optimization: {
            minimize: !DEBUG,
        }
    }
}
