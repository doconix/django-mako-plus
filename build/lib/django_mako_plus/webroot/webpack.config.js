const path = require('path');


module.exports = (env, argv) => {
    let DEBUG = argv.mode != 'production';
    return {
        entry: [
            './dmp-common.src.js',
        ],
        output: {
            path: path.resolve(__dirname),
            filename: DEBUG ? './dmp-common.js' : './dmp-common.min.js',
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
