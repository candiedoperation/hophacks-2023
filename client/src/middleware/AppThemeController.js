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

import { createTheme } from "@mui/material";
const themeChangeEvent = new Event("appthemechanged");

const toggleTheme = (emitter) => {
    (localStorage.getItem("theme") === null) ?
        localStorage.setItem("theme", "light") :
        localStorage.setItem("theme", (localStorage.getItem("theme") === 'light') ? 'dark' : 'light')

    if(emitter)
        emitter.dispatchEvent(themeChangeEvent);
}

const getCurrentTheme = () => {
    if (localStorage.getItem("theme") === null) localStorage.setItem("theme", "light")
    return localStorage.getItem('theme');
}

const setCurrentTheme = (theme) => {
    localStorage.setItem("theme", theme);
}

const getCurrentThemeComponent = () => {
    let paletteLight = {
        mode: 'light',
        primary: {
            main: "#7E57C2"
        },
        secondary: {
            main: "#E8BA12",
        },
        display: {
            main: "#FFFFFF",
            warning: "#E8BA12",
            contrastText: "#000000"
        }
    };

    let paletteDark = {
        mode: 'dark',
        primary: {
            main: "#FFC627"
        },
        secondary: {
            main: "#BA68C8",
        },
        display: {
            main: "#FFFFFF",
            warning: "#FFC627",
            contrastText: "#000000"
        },
    };

    switch (getCurrentTheme()) {
        case "light":
            return createTheme({
                palette: paletteLight
            })

        case "dark":
            return createTheme({
                palette: paletteDark
            });
    }
}

export { toggleTheme, getCurrentTheme, setCurrentTheme, getCurrentThemeComponent }