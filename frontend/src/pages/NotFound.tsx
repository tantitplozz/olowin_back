import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="text-center p-8 max-w-md">
        <div className="text-6xl font-bold text-gray-300 mb-4">404</div>
        <h1 className="text-3xl font-bold mb-4 text-gray-800">Page Not Found</h1>
        <p className="text-gray-600 mb-8">
          The page you are looking for doesn't exist or has been moved.
        </p>
        <Link
          to="/"
          className="btn btn-primary inline-block"
        >
          Return Home
        </Link>
      </div>
    </div>
  );
};

export default NotFound; 