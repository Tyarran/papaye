import { combineReducers, createStore } from 'redux';
import testReducer, {SecondReducer} from './test';

const reducer = combineReducers({testReducer, SecondReducer});
const store = createStore(reducer);
export default store;

