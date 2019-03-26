var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
define(["require", "exports", "nativescript-vue"], function (require, exports, nativescript_vue_1) {
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var BaseVueComponent = /** @class */ (function (_super) {
        __extends(BaseVueComponent, _super);
        function BaseVueComponent() {
            return _super !== null && _super.apply(this, arguments) || this;
        }
        return BaseVueComponent;
    }(nativescript_vue_1.default));
    exports.default = BaseVueComponent;
    var Home = /** @class */ (function (_super) {
        __extends(Home, _super);
        function Home() {
            return _super !== null && _super.apply(this, arguments) || this;
        }
        return Home;
    }(BaseVueComponent));
    exports.Home = Home;
    new nativescript_vue_1.default({
        template: "\n        <Frame>\n            <Home />\n        </Frame>",
        components: {
            Home: Home
        }
    }).$start();
});
