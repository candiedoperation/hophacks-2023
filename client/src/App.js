/*
    Satellite Imagery Based Community Assistance (HopHacks 2023)
    Copyright (C) 2023  SIBCA Contributors

    SIBCA Contributors:
        Kushal Kapoor (kushalk@umd.edu)
        Atheesh Thirumalairajan (atheesh@umd.edu)
        Tanay Shah (tanay11@umd.edu)
        Krish Bhatt (kbhatt20@umd.edu)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

import * as React from 'react';
import DashboardLayout from './integrals/DashboardLayout';
import { getCurrentTheme, getCurrentThemeComponent, toggleTheme } from './middleware/AppThemeController';
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { ThemeProvider } from '@emotion/react';
import { CssBaseline } from '@mui/material';
import LoginPage from './integrals/LoginPage';

const AuthRequired = (props) => {
  return (
    (sessionStorage.getItem("auth") == "true") ? props.children : <Navigate to="/login" />
  );
}

const PreAuthenticated = (props) => {
  return (
    (sessionStorage.getItem("auth") == "true") ? <Navigate to="/" /> : props.children
  );
}

const App = () => {
  const [themeMode, setThemeMode] = React.useState(getCurrentTheme());
  const [appTheme, setAppTheme] = React.useState(getCurrentThemeComponent())

  React.useEffect(() => {
    setAppTheme(getCurrentThemeComponent());

    /* Update Auth Status */
    if (sessionStorage.getItem("auth") == null) {
      sessionStorage.setItem("auth", "false");
    }
  }, [themeMode])

  const toggleThemeWrapper = () => {
    toggleTheme(window);
    setThemeMode(getCurrentTheme());
  }

  return (
    <ThemeProvider theme={appTheme}>
      <CssBaseline />
      <Routes>
        <Route path='/*' element={<AuthRequired><DashboardLayout toggleTheme={toggleThemeWrapper} /></AuthRequired>} />
        <Route path='/login' element={<PreAuthenticated><LoginPage /></PreAuthenticated>} />
      </Routes>
    </ThemeProvider>
  );
}

export default App;