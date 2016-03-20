var autoprefixer = require('autoprefixer');

module.exports = {
    entry: './src/app.js',
    output: {
        path: './dist',
        publicPath: "/static/dist/",
        filename: 'bundle.js'
    },
    module: {
        loaders: [
            { test: /\.scss$/, loaders: ["style", "css", "sass", "postcss"] },
            { test: /\.css$/, loader: 'style!css'},
            { test: /\.png$/, loader: "url-loader?limit=100000" },
            { test: /\.jpg$/, loader: "file-loader" }
        ]
    },
    postcss: function () {
        return [autoprefixer];
    }
};