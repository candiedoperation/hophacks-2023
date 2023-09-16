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
import { styled, useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import MuiDrawer from '@mui/material/Drawer';
import MuiAppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import CssBaseline from '@mui/material/CssBaseline';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import MapIcon from '@mui/icons-material/Map';
import SatelliteAltIcon from '@mui/icons-material/SatelliteAlt';
import CopyrightIcon from '@mui/icons-material/Copyright';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import WorldMapDashboard from './WorldMapDashboard';
import RegionAnalysisDashboard from './RegionAnalysisDashboard';
import { getCurrentTheme } from '../middleware/AppThemeController';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';

const drawerWidth = 240;
const openedMixin = (theme) => ({
    width: drawerWidth,
    transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
    }),
    overflowX: 'hidden',
});

const closedMixin = (theme) => ({
    transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
    }),
    overflowX: 'hidden',
    width: `calc(${theme.spacing(7)} + 1px)`,
    [theme.breakpoints.up('sm')]: {
        width: `calc(${theme.spacing(8)} + 1px)`,
    },
});

const DrawerHeader = styled('div')(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
}));

const AppBar = styled(MuiAppBar, {
    shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
    }),
    ...(open && {
        marginLeft: drawerWidth,
        width: `calc(100% - ${drawerWidth}px)`,
        transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    }),
}));

const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
    ({ theme, open }) => ({
        width: drawerWidth,
        flexShrink: 0,
        whiteSpace: 'nowrap',
        boxSizing: 'border-box',
        ...(open && {
            ...openedMixin(theme),
            '& .MuiDrawer-paper': openedMixin(theme),
        }),
        ...(!open && {
            ...closedMixin(theme),
            '& .MuiDrawer-paper': closedMixin(theme),
        }),
    }),
);

const DashboardLayout = (props) => {
    const theme = useTheme();
    const location = useLocation();
    const navigate = useNavigate();
    const [open, setOpen] = React.useState(false);
    const [pageTitle, setPageTitle] = React.useState("");
    const [drawerItems, setDrawerItems] = React.useState([]);

    const handleDrawerOpen = () => {
        setOpen(true);
    };

    const handleDrawerClose = () => {
        setOpen(false);
    };

    const parsePageTitle = (path) => {
        switch (path.substring(1)) {
            case 'world':
                return "World Map";

            case 'region':
                return "Region Analysis";

            case 'licenses':
                return "Licenses";

            default:
                return "Dashboard";
        }
    }

    React.useEffect(() => {
        /* Add Drawer Items */
        setDrawerItems((dI) => ([
            { primary: "World Map", path: "/world", icon: <MapIcon /> },
            { primary: "Region Analysis", path: "/region", icon: <SatelliteAltIcon /> },
            { primary: "Licenses", path: "/licenses", icon: <CopyrightIcon /> }
        ]));
    }, []);

    React.useEffect(() => {
        /* Set AppBar Title */
        setPageTitle(parsePageTitle(location.pathname));
    }, [location]);

    return (
        <Box sx={{ display: 'flex', height: '100%' }}>
            <CssBaseline />
            <AppBar sx={{ bgcolor: 'background.default', color: 'text.primary' }} elevation={0} position="fixed" open={open}>
                <Toolbar>
                    <IconButton
                        color="inherit"
                        aria-label="open drawer"
                        onClick={handleDrawerOpen}
                        edge="start"
                        sx={{
                            marginRight: 5,
                            ...(open && { display: 'none' }),
                        }}
                    >
                        <MenuIcon />
                    </IconButton>
                    <Box sx={{ display: 'flex', flexGrow: 1 }}>
                        <img src='/favicon-32x32.png' style={{ maxHeight: '32px', borderRadius: '5px' }} />
                        <Typography sx={{ marginLeft: '10px' }} variant="h6" noWrap component="div">
                            { pageTitle }
                        </Typography>
                    </Box>
                    <IconButton onClick={props.toggleTheme}>
                        { getCurrentTheme() == "light" ? <DarkModeIcon /> : <LightModeIcon /> }
                    </IconButton>
                </Toolbar>
                <Divider />
            </AppBar>
            <Drawer variant="permanent" open={open}>
                <DrawerHeader>
                    <IconButton onClick={handleDrawerClose}>
                        {theme.direction === 'rtl' ? <ChevronRightIcon /> : <ChevronLeftIcon />}
                    </IconButton>
                </DrawerHeader>
                <Divider />
                <List>
                    {drawerItems.map((drawerItem, key) => (
                        <ListItem key={key} disablePadding sx={{ display: 'block' }}>
                            <ListItemButton
                                onClick={() => { navigate(drawerItem.path); }}
                                sx={{
                                    minHeight: 48,
                                    justifyContent: open ? 'initial' : 'center',
                                    px: 2.5,
                                }}
                            >
                                <ListItemIcon
                                    sx={{
                                        minWidth: 0,
                                        mr: open ? 3 : 'auto',
                                        justifyContent: 'center',
                                    }}
                                >
                                    {drawerItem.icon}
                                </ListItemIcon>
                                <ListItemText primary={drawerItem.primary} sx={{ opacity: open ? 1 : 0 }} />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>
            </Drawer>
            <Box sx={{ flexGrow: 1, marginTop: '64px' }}>
                <Routes>
                    <Route path='/' element={<Navigate to="/world" />} exact />
                    <Route path='/world' element={<WorldMapDashboard />} exact />
                    <Route path='/region' element={<RegionAnalysisDashboard />} exact />
                </Routes>
            </Box>
        </Box>
    )
}

export default DashboardLayout;