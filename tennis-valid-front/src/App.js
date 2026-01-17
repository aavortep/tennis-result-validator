//import logo from './logo.svg';
import './App.css';
import { Route, Routes, Navigate, BrowserRouter as Router } from 'react-router-dom';
import LoginPage from './pages/login.js';
import SignupPage from './pages/signup.js';

function App() {
  return (
    <div>
      <main>
        <Router>
          <Routes>
            <Route path='/login' element={<LoginPage/>} />
            <Route path='/signup' element={<SignupPage/>} />
            <Route exact path='/' element={<Navigate replace to='/login' />} />
          </Routes>
        </Router>
      </main>
    </div>
  );
}

export default App;
