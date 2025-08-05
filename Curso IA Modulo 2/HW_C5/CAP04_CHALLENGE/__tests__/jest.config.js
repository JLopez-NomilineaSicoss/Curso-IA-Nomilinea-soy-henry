const nextJest = require('next/jest');

// Providing the path to your Next.js app to load next.config.js and .env files in your test environment
const createJestConfig = nextJest({
  dir: './', // this is the 'rootDir' and should point to the root of your Next.js project
});

const customJestConfig = {
  rootDir: './', // Add this line if Jest does not recognize the root directory
  coverageProvider: "v8",
  testEnvironment: "jsdom",
  // ... other options
};

// Make sure you don't export the custom config directly, but call the createJestConfig function with the custom config
module.exports = createJestConfig(customJestConfig);