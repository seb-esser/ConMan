// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Vuetify
import {createVuetify} from 'vuetify'
import {mdi} from "vuetify/lib/iconsets/mdi";
import {aliases} from "vuetify/lib/iconsets/fa";

export default createVuetify(
    // https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
    {
        icons: {
            defaultSet: 'mdi',
            aliases,
            sets: {
                mdi,
            }
        },
        theme: {
            themes: {
                light: {
                    primary: '#0065bd',
                    secondary: '#005293',
                    accent: '#E37222',
                    error: '#b71c1c',
                },
            },
        },
    }
)
