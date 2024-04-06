import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js'

// Copied from videohelpersuite
// https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/blob/ca8494b38006c76f5b0f02eade284998dbab011e/web/js/VHS.core.js

function chainCallback(object, property, callback) {
    if (object == undefined) {
        //This should not happen.
        console.error("Tried to add callback to non-existant object")
        return;
    }
    if (property in object) {
        const callback_orig = object[property]
        object[property] = function () {
            const r = callback_orig.apply(this, arguments);
            callback.apply(this, arguments);
            return r
        };
    } else {
        object[property] = callback;
    }
}

function addAudioPreview(nodeType) {
    chainCallback(nodeType.prototype, "onNodeCreated", function () {
        var element = document.createElement("div");
        const previewNode = this;
        var previewWidget = this.addDOMWidget("audiopreview", "preview", element, {
            serialize: false,
            hideOnZoom: false,
            getValue() {
                return element.value;
            },
            setValue(v) {
                element.value = v;
            },
        });

        // element.style['pointer-events'] = "none"
        previewWidget.value = { hidden: false, paused: false, params: {} }
        previewWidget.parentEl = document.createElement("div");
        previewWidget.parentEl.className = "pronodes_preview";
        previewWidget.parentEl.style['width'] = "100%"
        element.appendChild(previewWidget.parentEl);
        previewWidget.audioEl = document.createElement("audio");
        previewWidget.audioEl.controls = true;
        // previewWidget.audioEl.muted = true;
        previewWidget.audioEl.style['width'] = "100%"


        this.updateParameters = (params, force_update) => {
            if (!previewWidget.value.params) {
                if (typeof (previewWidget.value != 'object')) {
                    previewWidget.value = { hidden: false, paused: false }
                }
                previewWidget.value.params = {}
            }
            Object.assign(previewWidget.value.params, params)

            if (force_update) {
                previewWidget.updateSource();
            }
        };
        previewWidget.updateSource = function () {
            if (this.value.params == undefined) {
                return;
            }
            let params = {}
            Object.assign(params, this.value.params);//shallow copy
            this.parentEl.hidden = this.value.hidden;

            if (params.previews) {

                previewWidget.audioEl.src = api.apiURL('/view?' + new URLSearchParams(params.previews[0]));

                this.audioEl.hidden = false;
            } else {
                this.audioEl.hidden = true;
            }
        }
        previewWidget.parentEl.appendChild(previewWidget.audioEl)
    });
}

app.registerExtension({
    name: "piperTTS.audio_preview",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {


        if (nodeData?.name == "PiperTTS") {
            chainCallback(nodeType.prototype, "onExecuted", function (message) {
                if (message?.previews) {
                    this.updateParameters(message, true);
                }
            });
            addAudioPreview(nodeType);

            //Hide the information passing 'preview' output
            //TODO: check how this is implemented for save image
            chainCallback(nodeType.prototype, "onNodeCreated", function () {
                this.setSize([350, 250]);
                this._outputs = this.outputs
                Object.defineProperty(this, "outputs", {
                    set: function (value) {
                        this._outputs = value;
                        requestAnimationFrame(() => {
                            if (app.nodeOutputs[this.id + ""]) {
                                this.updateParameters(app.nodeOutputs[this.id + ""], true);
                            }
                        })
                    },
                    get: function () {
                        return this._outputs;
                    }
                });
                //Display previews after reload/ loading workflow
                requestAnimationFrame(() => { this.updateParameters({}, true); });
            });
        }
    },
});