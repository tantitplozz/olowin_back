import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <h3 className="text-xl font-bold mb-2">OmniCard AI</h3>
            <p className="text-gray-400">
              Multi-Agent System for AI-powered data processing
            </p>
          </div>
          
          <div className="mb-4 md:mb-0">
            <h4 className="font-semibold mb-2">Quick Links</h4>
            <nav className="flex flex-col">
              <Link to="/" className="text-gray-400 hover:text-white mb-1">Home</Link>
              <Link to="/dashboard" className="text-gray-400 hover:text-white mb-1">Dashboard</Link>
              <a 
                href="https://github.com/tantitplozz/olowin_back" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white mb-1"
              >
                GitHub
              </a>
            </nav>
          </div>
          
          <div>
            <h4 className="font-semibold mb-2">Contact</h4>
            <p className="text-gray-400">Email: info@omnicard.ai</p>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-6 pt-6 text-center text-gray-400">
          <p>&copy; {currentYear} OmniCard AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
