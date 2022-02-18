import apiService from "./api";

class CardTemplateServices {
    async getCardTemplates() {
        const response = await apiService.get("cueSearch/templates/");
        if (response.success) {
            return response.data
        }
        else {
            return response
        }
    }
    async addCardTemplate(payload) {
        const response = await apiService.post("cueSearch/templates/create/", payload);
        if (response.success) {
            return response
        }
        else {
            return response
        }
    }
    async updateCardTemplate(id, payload) {
        const response = await apiService.post("cueSearch/templates/update/" + id, payload);
        if (response.success) {
            return response
        }
        else {
            return response
        }
    }
    async publishCardTemplate(payload) {
        const response = await apiService.post("cueSearch/templates/publish/", payload);
        if (response.success) {
            return response
        }
        else {
            return response
        }
    }
    async deleteCardTemplate(id) {
        const response = await apiService.delete("cueSearch/templates/delete/" + id);
        if (response.success) {
            return response
        }
        else {
            return response
        }
    }



}


let cardTemplateServices = new CardTemplateServices();
export default cardTemplateServices;
