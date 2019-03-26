import Vue from "nativescript-vue";

export default class BaseVueComponent extends Vue {
}

export class Home extends BaseVueComponent {
}

new Vue({

    template: `
        <Frame>
            <Home />
        </Frame>`,

    components: {
        Home
    }
}).$start();
