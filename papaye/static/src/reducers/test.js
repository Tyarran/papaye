const testReducer = (state=window.state, action) => {
    console.log(state);
    const newState = Object.assign({}, state);
    switch (action.type) {
    case 'CHOSE':
        newState.simpleUrl = action.url;
        return newState;
    case 'TOGGLE_MENU_BURGER_VISIBILITY':
        newState.navbarBurgerIsActive = action.navbarBurgerIsActive;
        return newState;
    default:
        return state;
    }
};

export default testReducer;

export const SecondReducer = (state=0, action) => { return state; };
