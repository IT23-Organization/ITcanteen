import { createSlice } from '@reduxjs/toolkit'

export const userSlice = createSlice({
    name: 'user',
    initialState: {
        username: '',
        user_id: 0,
        store_id: 0,
    },
    reducers: {
        setUser(state, action) {
            state.username = action.payload.username
            state.user_id = action.payload.user_id
            state.store_id = action.payload.store_id
        },
        clearUser(state) {
            state.username = ''
            state.user_id = 0
            state.store_id = 0
        },
    },
})

export const { setUser, clearUser } = userSlice.actions

export default userSlice.reducer