import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [searchCriteria, setSearchCriteria] = useState({
    location: '',
    propertyType: 'appartement',
    rooms: '',
    minSurface: '',
    maxSurface: '',
    minPrice: '',
    maxPrice: '',
    furnished: '',
    charges: 'excluded',
    bedrooms: '',
    floor: '',
    balcony: false,
    parking: false,
    pets: false
  });

  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('price');
  const [favorites, setFavorites] = useState([]);

  // Sample data for demo
  const sampleListings = [
    {
      id: '1',
      title: 'Appartement 2 pièces - Centre Paris',
      price: 1200,
      surface: 45,
      rooms: 2,
      bedrooms: 1,
      address: '75001 Paris, Île-de-France',
      description: 'Magnifique appartement au cœur de Paris, proche des transports.',
      images: ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400'],
      source: 'LeBonCoin',
      publishedAt: '2025-03-15',
      furnished: true,
      charges: 150,
      floor: 3,
      balcony: true,
      parking: false,
      pets: false
    },
    {
      id: '2',
      title: 'Studio meublé - Quartier Latin',
      price: 850,
      surface: 25,
      rooms: 1,
      bedrooms: 0,
      address: '75005 Paris, Île-de-France',
      description: 'Studio lumineux dans le quartier historique, idéal étudiant.',
      images: ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400'],
      source: 'SeLoger',
      publishedAt: '2025-03-14',
      furnished: true,
      charges: 100,
      floor: 2,
      balcony: false,
      parking: false,
      pets: true
    },
    {
      id: '3',
      title: 'Appartement 3 pièces avec terrasse',
      price: 1800,
      surface: 70,
      rooms: 3,
      bedrooms: 2,
      address: '92100 Boulogne-Billancourt, Île-de-France',
      description: 'Spacieux appartement avec terrasse, parking inclus.',
      images: ['https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400'],
      source: 'Foncia',
      publishedAt: '2025-03-13',
      furnished: false,
      charges: 200,
      floor: 5,
      balcony: true,
      parking: true,
      pets: false
    }
  ];

  const handleSearch = async () => {
    setLoading(true);
    // Simulate API call delay
    setTimeout(() => {
      setListings(sampleListings.filter(listing => {
        if (searchCriteria.location && !listing.address.toLowerCase().includes(searchCriteria.location.toLowerCase())) {
          return false;
        }
        if (searchCriteria.rooms && listing.rooms < parseInt(searchCriteria.rooms)) {
          return false;
        }
        if (searchCriteria.minPrice && listing.price < parseInt(searchCriteria.minPrice)) {
          return false;
        }
        if (searchCriteria.maxPrice && listing.price > parseInt(searchCriteria.maxPrice)) {
          return false;
        }
        if (searchCriteria.minSurface && listing.surface < parseInt(searchCriteria.minSurface)) {
          return false;
        }
        if (searchCriteria.maxSurface && listing.surface > parseInt(searchCriteria.maxSurface)) {
          return false;
        }
        return true;
      }));
      setLoading(false);
    }, 1000);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSearchCriteria(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const toggleFavorite = (listingId) => {
    setFavorites(prev => 
      prev.includes(listingId) 
        ? prev.filter(id => id !== listingId)
        : [...prev, listingId]
    );
  };

  const sortedListings = [...listings].sort((a, b) => {
    switch (sortBy) {
      case 'price':
        return a.price - b.price;
      case 'surface':
        return b.surface - a.surface;
      case 'date':
        return new Date(b.publishedAt) - new Date(a.publishedAt);
      default:
        return 0;
    }
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-blue-600">🏠 PromptIA</h1>
            <nav className="flex space-x-6">
              <a href="#" className="text-gray-600 hover:text-blue-600">Recherche</a>
              <a href="#" className="text-gray-600 hover:text-blue-600">Favoris ({favorites.length})</a>
              <a href="#" className="text-gray-600 hover:text-blue-600">Alertes</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="absolute inset-0">
          <img 
            src="https://images.unsplash.com/photo-1697994391342-dda8bdff0211?w=1200" 
            alt="Appartements français"
            className="w-full h-full object-cover opacity-20"
          />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <h2 className="text-5xl font-bold mb-4">Trouvez votre appartement idéal</h2>
          <p className="text-xl mb-8">Recherchez parmi des milliers d'annonces de location en France</p>
        </div>
      </section>

      {/* Search Form */}
      <section className="bg-white shadow-lg -mt-10 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Localisation</label>
              <input
                type="text"
                name="location"
                value={searchCriteria.location}
                onChange={handleInputChange}
                placeholder="Paris, Lyon, Marseille..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type de bien</label>
              <select
                name="propertyType"
                value={searchCriteria.propertyType}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="appartement">Appartement</option>
                <option value="maison">Maison</option>
                <option value="studio">Studio</option>
                <option value="loft">Loft</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nombre de pièces</label>
              <select
                name="rooms"
                value={searchCriteria.rooms}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Indifférent</option>
                <option value="1">1 pièce</option>
                <option value="2">2 pièces</option>
                <option value="3">3 pièces</option>
                <option value="4">4 pièces</option>
                <option value="5">5+ pièces</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Budget (€/mois)</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  name="minPrice"
                  value={searchCriteria.minPrice}
                  onChange={handleInputChange}
                  placeholder="Min"
                  className="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  name="maxPrice"
                  value={searchCriteria.maxPrice}
                  onChange={handleInputChange}
                  placeholder="Max"
                  className="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Surface (m²)</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  name="minSurface"
                  value={searchCriteria.minSurface}
                  onChange={handleInputChange}
                  placeholder="Min"
                  className="w-1/2 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm"
                />
                <input
                  type="number"
                  name="maxSurface"
                  value={searchCriteria.maxSurface}
                  onChange={handleInputChange}
                  placeholder="Max"
                  className="w-1/2 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Meublé</label>
              <select
                name="furnished"
                value={searchCriteria.furnished}
                onChange={handleInputChange}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Indifférent</option>
                <option value="true">Meublé</option>
                <option value="false">Non meublé</option>
              </select>
            </div>

            <div className="flex items-end space-x-4">
              <label className="flex items-center text-sm">
                <input
                  type="checkbox"
                  name="balcony"
                  checked={searchCriteria.balcony}
                  onChange={handleInputChange}
                  className="mr-2 text-blue-600"
                />
                Balcon/Terrasse
              </label>
            </div>

            <div className="flex items-end space-x-4">
              <label className="flex items-center text-sm">
                <input
                  type="checkbox"
                  name="parking"
                  checked={searchCriteria.parking}
                  onChange={handleInputChange}
                  className="mr-2 text-blue-600"
                />
                Parking
              </label>
            </div>

            <div className="flex items-end space-x-4">
              <label className="flex items-center text-sm">
                <input
                  type="checkbox"
                  name="pets"
                  checked={searchCriteria.pets}
                  onChange={handleInputChange}
                  className="mr-2 text-blue-600"
                />
                Animaux OK
              </label>
            </div>

            <div className="flex items-end">
              <button
                onClick={handleSearch}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              >
                🔍 Rechercher
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Results Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {listings.length > 0 && (
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-2xl font-bold text-gray-900">
              {listings.length} annonce{listings.length > 1 ? 's' : ''} trouvée{listings.length > 1 ? 's' : ''}
            </h3>
            
            <div className="flex items-center space-x-4">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="price">Prix croissant</option>
                <option value="surface">Surface décroissante</option>
                <option value="date">Plus récent</option>
              </select>
              
              <div className="flex rounded-md border border-gray-300">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-3 py-2 ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                >
                  ⊞ Grille
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-2 ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                >
                  ☰ Liste
                </button>
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {!loading && sortedListings.length === 0 && listings.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Utilisez le formulaire ci-dessus pour rechercher des appartements</p>
          </div>
        )}

        {!loading && viewMode === 'grid' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedListings.map(listing => (
              <div key={listing.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="relative">
                  <img 
                    src={listing.images[0]} 
                    alt={listing.title}
                    className="w-full h-48 object-cover"
                  />
                  <button
                    onClick={() => toggleFavorite(listing.id)}
                    className={`absolute top-3 right-3 p-2 rounded-full ${
                      favorites.includes(listing.id) ? 'bg-red-500 text-white' : 'bg-white text-gray-600'
                    } hover:scale-110 transition-transform`}
                  >
                    ♥
                  </button>
                  <div className="absolute bottom-3 left-3 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm">
                    {listing.source}
                  </div>
                </div>
                
                <div className="p-4">
                  <h4 className="font-bold text-lg mb-2 text-gray-900">{listing.title}</h4>
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">{listing.description}</p>
                  
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-2xl font-bold text-blue-600">{listing.price}€/mois</span>
                    <span className="text-gray-500">{listing.surface}m² • {listing.rooms} pièces</span>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-500 mb-3">
                    <span>📍 {listing.address}</span>
                  </div>
                  
                  <div className="flex flex-wrap gap-2 mb-3">
                    {listing.furnished && <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">Meublé</span>}
                    {listing.balcony && <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">Balcon</span>}
                    {listing.parking && <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">Parking</span>}
                    {listing.pets && <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs">Animaux OK</span>}
                  </div>
                  
                  <button className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors">
                    Voir l'annonce
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && viewMode === 'list' && (
          <div className="space-y-4">
            {sortedListings.map(listing => (
              <div key={listing.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="relative md:w-64 h-48">
                    <img 
                      src={listing.images[0]} 
                      alt={listing.title}
                      className="w-full h-full object-cover rounded-lg"
                    />
                    <button
                      onClick={() => toggleFavorite(listing.id)}
                      className={`absolute top-3 right-3 p-2 rounded-full ${
                        favorites.includes(listing.id) ? 'bg-red-500 text-white' : 'bg-white text-gray-600'
                      } hover:scale-110 transition-transform`}
                    >
                      ♥
                    </button>
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-bold text-xl text-gray-900">{listing.title}</h4>
                      <span className="bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm">
                        {listing.source}
                      </span>
                    </div>
                    
                    <p className="text-gray-600 mb-3">{listing.description}</p>
                    
                    <div className="flex flex-wrap items-center gap-4 mb-3">
                      <span className="text-2xl font-bold text-blue-600">{listing.price}€/mois</span>
                      <span className="text-gray-500">{listing.surface}m²</span>
                      <span className="text-gray-500">{listing.rooms} pièces</span>
                      <span className="text-gray-500">📍 {listing.address}</span>
                    </div>
                    
                    <div className="flex flex-wrap gap-2 mb-4">
                      {listing.furnished && <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">Meublé</span>}
                      {listing.balcony && <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">Balcon</span>}
                      {listing.parking && <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">Parking</span>}
                      {listing.pets && <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs">Animaux OK</span>}
                    </div>
                    
                    <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors">
                      Voir l'annonce
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default App;