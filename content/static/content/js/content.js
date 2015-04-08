var content = angular.module('content', ["autocompleteSearch"]);

var fileTemplate = {
    url: '',
    file_id: '',
    title: ''
};

var dataTemplates = {
    'text': {
        content_type: 'text',
        content: '',
    },
    'toggle': {
        content_type: 'toggle',
        content: '',
        toggle: '',
    },
    'toggleset': {
        content_type: 'toggleset',
        content: {
            variable_name: '',
            label: '',
            value: '',
            alternatives: [],
        },
    },
    'togglesetmulti': {
        content_type: 'togglesetmulti',
        content: {
            variable_name: '',
            label: '',
            value: [],
            alternatives: [],
        },
    },
    'conditionalset': {
        content_type: 'conditionalset',
        content: [],
    },
    'conditionaltext': {
        conditions: [{
            var_name: '',
            logical_operator: '',
            operator: '',
            value: ''
        }],
        content: '',
    },
    'condition': {
        var_name: '',
        logical_operator: '',
        operator: '',
        value: ''
    },
    'form': {
        content_type: 'form',
        content: []
    },
    'quiz': {
        content_type: 'quiz',
        content: []
    },
    'image': {
        content_type: 'image',
        content: fileTemplate
    },
    'video': {
        content_type: 'video',
        content: fileTemplate
    },
    'audio': {
        content_type: 'audio',
        content: fileTemplate
    },
    'file': {
        content_type: 'file',
        content: fileTemplate
    },
    'toggleitem': {
        label: '',
        value: '',
        text: '',
    },
    'numeric': {
        field_type: 'numeric',
        variable_name: '',
        label: '',
        required: false,
    },
    'string': {
        field_type: 'string',
        variable_name: '',
        label: '',
        required: false,
    },
    'textarea': {
        field_type: 'text',
        variable_name: '',
        label: '',
        required: false,
    },
    'multiplechoice': {
        field_type: 'multiplechoice',
        variable_name: '',
        label: '',
        required: false,
        alternatives: []
    },
    'multipleselection': {
        field_type: 'multipleselection',
        variable_name: '',
        label: '',
        required: false,
        value: [],
        alternatives: []
    },
    'hiddenfield': {
        field_type: 'hiddenfield',
        variable_name: '',
    },
    'question': {
        question: '',
        variable_name: '',
        right: '',
        wrong: '',
        alternatives: [],
    },
    'alternative': {
        label: '',
        value: '',
    },
};

content.run(['$rootScope', '$http', function(scope, http) {
    if (!initData) {
        scope.data = [];
    } else {
        scope.data = initData;
    }

    scope.variables = [];
    http.get('/api/system/variables/').success(function(data) {
        scope.variables = data;
    });
}]);

content.controller('contentArray', ['$scope', function(scope) {

    scope.logical_operators = ['AND', 'OR'];
    scope.add = function(array, type) {
        array.push(angular.copy(dataTemplates[type]));
    };

    scope.up = function(array, index) {
        array.splice(index--, 0, array.splice(index, 1)[0]);
    };

    scope.down = function(array, index) {
        array.splice(index++, 0, array.splice(index, 1)[0]);
    };

    scope.delete = function(array, index) {
        array.splice(index, 1);
    };
}]);

content.controller('markdown', ['$scope', '$window', '$sce', function(scope, window, sce) {
    scope.html = '';
    scope.md2html = function(content) {
        var marked = window.marked(content);
        marked = marked.replace(/({{.*?}})/g, '<span class="markup">$&</span>');
        scope.html = sce.trustAsHtml(marked);
    };
}]);

content.directive('markdownText', ['$timeout', function(timeout) {
    return {
        restrict: 'C',
        require: 'ngModel',
        controller: 'markdown',
        link: function(scope, elem, attrs, ngModel) {
            timeout(function() {
                scope.md2html(ngModel.$modelValue);
            });
            ngModel.$viewChangeListeners.push(function() {
                scope.md2html(ngModel.$modelValue);
            });
        }
    };
}]);

content.directive('textarea', function() {
    // autoresize textarea as you type.
    return {
        restrict: 'E',
        link: function(scope, elem, attrs) {
            var threshold    = 40,
                minHeight    = elem[0].offsetHeight,
                paddingLeft  = elem.css('paddingLeft'),
                paddingRight = elem.css('paddingRight');

            var shadow = angular.element('<div></div>').css({
                position:   'absolute',
                top:        -10000,
                left:       -10000,
                width:      elem[0].offsetWidth - parseInt(paddingLeft || 0, 10) - parseInt(paddingRight || 0, 10),
                fontSize:   elem.css('fontSize'),
                fontFamily: elem.css('fontFamily'),
                lineHeight: elem.css('lineHeight'),
                resize:     'none'
            });

            angular.element(document.body).append(shadow);

            var update = function() {
                var times = function(string, number) {
                    for (var i = 0, r = ''; i < number; i++) {
                        r += string;
                    }
                    return r;
                };

                var val = elem.val().replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/&/g, '&amp;')
                    .replace(/\n$/, '<br/>&nbsp;')
                    .replace(/\n/g, '<br/>')
                    .replace(/\s{2,}/g, function(space) {
                        return times('&nbsp;', space.length - 1) + ' ';
                    });

                shadow.html(val);
                elem.css('height', Math.max(shadow[0].offsetHeight + threshold , minHeight));
                angular.element(elem[0].nextSibling).css('height', elem.css('height'));
            };

            scope.$on('$destroy', function() {
                shadow.remove();
            });

            elem.bind('keyup keydown keypress change', update);

            if (attrs.ngModel) {
               scope.$watch(attrs.ngModel, update);
            }
        }
    };
});

content.directive('filer', ['$compile', '$http', function(compile, http) {
    return {
        restrict: 'C',
        replace: true,
        link: function(scope, elem, attrs) {
            scope.noimg = elem.find('#id_file_thumbnail_img').attr('src');
            scope.index = scope.$parent.$index;

            // clear on click
            elem.find('#id_file_clear').addClass('clear').on('click', function() {
                elem.find('#id_file_' + scope.index ).removeAttr('value');
                elem.find('#id_file_' + scope.index + '_thumbnail_img').attr('src', scope.noimg);
                elem.find('#id_file_' + scope.index + '_description_txt').html('');
                elem.find('#id_file_' + scope.index + '_clear').hide();
                scope.$apply(function() {
                    scope.pagelet.content.file_id = '';
                    scope.pagelet.content.url = '';
                })
            });

            // set ng-model
            var input = elem.find('#id_file')[0];
            if (input.id === 'id_file') {
                var file_id = angular.element(input).attr('ng-model', 'pagelet.content.file_id');
                compile(file_id)(scope);
            }

            // differentiate repeated elements
            elem.find('#id_file')[0].id = 'id_file_' + scope.index;
            elem.find('#id_file_thumbnail_img')[0].id = 'id_file_' + scope.index + '_thumbnail_img';
            elem.find('#id_file_description_txt')[0].id = 'id_file_' + scope.index + '_description_txt';
            elem.find('#id_file_clear')[0].id = 'id_file_' + scope.index + '_clear';
            elem.find('#lookup_id_file')[0].id = 'lookup_id_file_' + scope.index;

            scope.apiURL = filerApi + scope.pagelet.content_type + '/';

            // receive on select
            angular.element(window).bind('focus', function(val) {
                var value = elem.find('#id_file_' + scope.index).attr('value');
                if (value !== scope.pagelet.content.file_id) {
                    scope.$apply(function() {
                        scope.pagelet.content.file_id = value;
                    });
                    http.get(scope.apiURL + value).success(function(data) {
                        scope.pagelet.content.url = data['url'];
                    });
                }
            });

            // populate on load
            if (scope.pagelet.content.file_id !== '') {
                http.get(scope.apiURL + scope.pagelet.content.file_id).success(function(data) {
                    elem.find('#id_file_' + scope.index ).attr('value', data['id']);
                    elem.find('#id_file_' + scope.index + '_thumbnail_img').attr('src', data['thumbnail']);
                    elem.find('#id_file_' + scope.index + '_description_txt').html(data['description']);
                    elem.find('#id_file_' + scope.index + '_clear').show();
                });
            }
        }
    };
}]);

content.directive('optTitle', [function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            element.bind('mouseenter', function() {
                element[0].title = element.children(':selected')[0].title
            })
        }
    };
}]);
