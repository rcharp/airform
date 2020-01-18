module.exports = {
  source: './src',
  destination: './esdoc',
  plugins: [
    {
      name: 'esdoc-standard-plugin'
    },
    {
      name: 'esdoc-ecmascript-proposal-plugin',
      option: { all: true }
    }
  ]
};