import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section className="py-12 md:py-16 lg:py-20">
        <div className="flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 mb-8 md:mb-0 md:pr-12">
            <h1 className="text-4xl lg:text-5xl font-bold mb-4 text-gray-900">
              OmniCard AI
            </h1>
            <p className="text-xl text-gray-600 mb-6">
              Multi-Agent System for AI-powered data processing
            </p>
            <p className="text-gray-600 mb-8">
              OmniCard AI utilizes advanced agents and local LLMs to provide 
              intelligent data processing with maximum privacy and security.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link 
                to="/dashboard" 
                className="btn btn-primary"
              >
                Get Started
              </Link>
              <a 
                href="https://github.com/tantitplozz/olowin_back" 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn btn-secondary"
              >
                View on GitHub
              </a>
            </div>
          </div>
          <div className="md:w-1/2">
            <div className="bg-gray-200 rounded-lg p-8 text-center">
              <div className="text-5xl mb-4">🧠</div>
              <p className="text-gray-700">AI Agent Visualization Placeholder</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 border-t border-gray-200">
        <h2 className="text-3xl font-bold mb-8 text-center">Key Features</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="card">
            <div className="text-3xl mb-4 text-blue-500">🔍</div>
            <h3 className="text-xl font-semibold mb-2">Multi-Agent System</h3>
            <p className="text-gray-600">
              Specialized agents for various tasks working together in a coordinated workflow.
            </p>
          </div>
          <div className="card">
            <div className="text-3xl mb-4 text-blue-500">🖥️</div>
            <h3 className="text-xl font-semibold mb-2">Local LLM Support</h3>
            <p className="text-gray-600">
              Use Ollama or other local models for maximum privacy and control of your data.
            </p>
          </div>
          <div className="card">
            <div className="text-3xl mb-4 text-blue-500">📊</div>
            <h3 className="text-xl font-semibold mb-2">Real-time Monitoring</h3>
            <p className="text-gray-600">
              Monitor system performance and agent activities with advanced monitoring tools.
            </p>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-12 border-t border-gray-200">
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Experience the power of AI agents working together to process your data efficiently.
          </p>
          <Link 
            to="/dashboard" 
            className="btn btn-primary px-8 py-3 text-lg"
          >
            Try the Demo
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home; 