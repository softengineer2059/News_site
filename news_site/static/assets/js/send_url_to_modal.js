function send_url_to_modal_article(articleId) {
        var url = "article/delete_article/article_id".replace('article_id', articleId);
        document.getElementById('remove-link').setAttribute('action', url);
    }


function send_url_to_modal_category(categoryId) {
        var url = "/article/delete_category/category_id".replace('category_id', categoryId);// /-слеш в начале нужен для создания абсолютной ссылки
        document.getElementById('remove-link').setAttribute('action', url);
    }

function send_url_to_modal_category_edit(button) {
    var categoryId = button.getAttribute('data-category-id');
    var categoryName = button.getAttribute('data-category-name');
    var categorySlug = button.getAttribute('data-category-slug');

    var url = "/article/edit_category/" + categoryId;
    document.getElementById('edit-link').setAttribute('action', url);
    document.getElementById('input-name').setAttribute('value', categoryName);
    document.getElementById('input-slug').setAttribute('value', categorySlug);
}


function send_url_to_modal_subcategory(subcategoryId) {
        var url = "/article/delete_subcategory/subcategory_id".replace('subcategory_id', subcategoryId);
        document.getElementById('remove-link').setAttribute('action', url);
    }

function send_url_to_modal_subcategory_edit(button) {
    var subcategoryId = button.getAttribute('data-subcategory-id');
    var subcategoryName = button.getAttribute('data-subcategory-name');
    var subcategorySlug = button.getAttribute('data-subcategory-slug');

    var url = "/article/edit_subcategory/" + subcategoryId;
    document.getElementById('edit-form').setAttribute('action', url);
    document.getElementById('input-name').setAttribute('value', subcategoryName);
    document.getElementById('input-slug').setAttribute('value', subcategorySlug);
}


function send_url_to_modal_tag(tagsId) {
        var url = "/article/delete_tag/tags_id".replace('tags_id', tagsId);
        document.getElementById('remove-link').setAttribute('action', url);
    }

function send_url_to_modal_tag_edit(button) {
    var tagId = button.getAttribute('data-tag-id');
    var tagName = button.getAttribute('data-tag-name');
    var tagSlug = button.getAttribute('data-tag-slug');

    var url = "/article/edit_tag/" + tagId;
    document.getElementById('edit-link').setAttribute('action', url);
    document.getElementById('input-name').setAttribute('value', tagName);
    document.getElementById('input-slug').setAttribute('value', tagSlug);
}


function send_url_to_modal_country(countryId) {
        var url = "/article/delete_country/country_id".replace('country_id', countryId);// /-слеш в начале нужен для создания абсолютной ссылки
        document.getElementById('remove-link').setAttribute('action', url);
    }

function send_url_to_modal_country_edit(button) {
    var countryId = button.getAttribute('data-country-id');
    var countryName = button.getAttribute('data-country-name');
    var countrySlug = button.getAttribute('data-country-slug');

    var url = "/article/edit_country/" + countryId;
    document.getElementById('edit-link').setAttribute('action', url);
    document.getElementById('input-name').setAttribute('value', countryName);
    document.getElementById('input-slug').setAttribute('value', countrySlug);
}


function send_url_to_modal_remove_comment(itemId) {
        var url = "/comments/remove_comment/" + itemId + "/";
        document.getElementById('remove-link').setAttribute('action', url);
    }


function send_url_to_modal_reply(article_id, parent_id) {
    var url = '/comments/comment_reply/' + article_id + '/' + parent_id + '/';
    document.getElementById('reply-remove-link').setAttribute('action', url);
}