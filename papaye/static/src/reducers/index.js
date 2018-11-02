import actions from '../actions';

import _ from 'lodash';


const appReducer = (state, action) => {
    switch (action.type) {
    case actions.TOGGLE_MENU_BURGER_VISIBILITY.type:
        return state.set('navbarBurgerIsActive', action.navbarBurgerIsActive);
    case actions.ACTIVE_NAVBAR_ITEM.type:
        const newNavBarItems = _.map(state.get('navMenu'), (item) => {
            item.active = item.id === action.itemId;
            return item;
        });

        return state.set('navMenu', newNavBarItems);
    case 'DATA_FETCH':
        return state;
    case 'DATA_READ':
        let newState = state.set('packageList', action.response);
        return newState.set('filteredPackageList', action.response);
    case 'DATA_FILTER':
        const packageList = state.get('packageList');

        if (action.pattern === '') {
            return state.set('filteredPackageList', packageList);
        }

        const filtered = packageList.filter((pkg) => {
            return pkg.name.includes(action.pattern);
        });
        return state.set('filteredPackageList', filtered);
    default:
        return state;
    }
};


export default appReducer;
