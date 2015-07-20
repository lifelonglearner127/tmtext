var RR = function(href, id) {
    var _isArray = function(obj) {
        return Object.prototype.toString.call(obj) == '[object Array]';
    };
    var r3_entity = new r3_common(this);
    return {
        U: 'undefined',
        charset: 'UTF-8',
        D: 'a5d5af7012d61fd1',
        T: '632d581ca7b9feb3',
        TD: '3e89ae564e77b361',
        TM: '|61e8c5b5ec8a3a00|421363196daa3779|73de560159c8c3b9|f0f1949cb6ae84eb|752e69416232e918|cc53d80ef0c355a7|5120f20de7f2261b|',
        setCharset: function(c) {
            this.charset = c;
        },
        fixName: function(name) {
            var result = name;
            if (result.indexOf('&amp;') > -1) {
                result = result.replace(/&amp;/g, "&");
            }
            if (result.indexOf('&#039;') > -1) {
                result = result.replace(/&#039;/g, "'");
            }
            return result;
        },
        fixId: function(id) {
            var result = id;
            if (r3_entity.apiKey == this.D) {
                result = result.toUpperCase();
            }
            return result;
        },
        fixCatId: function(id) {
            return this.fixId(this.fixName(id));
        },
        l: href,
        id: id,
        lc: function(n) {
            if (n.indexOf('=') === -1) {
                n += '=';
            }
            if (n.indexOf('?') === -1 && n.indexOf('&') === -1) {
                var pidx = this.l.indexOf('?' + n);
                if (pidx === -1) {
                    pidx = this.l.indexOf('&' + n);
                }
                return pidx !== -1;
            } else {
                return (this.l.indexOf(n) !== -1);
            }
        },
        pq: function(n) {
            var pidx = this.l.indexOf("?" + n + '=');
            if (pidx == -1) {
                pidx = this.l.indexOf("&" + n + '=');
            }
            var v;
            if (pidx !== -1) {
                pidx++;
                var didx = this.l.indexOf("&", pidx);
                if (didx != -1) {
                    v = this.l.substring(pidx + n.length + 1, didx);
                } else {
                    v = this.l.substring(pidx + n.length + 1, this.l.length);
                }
            } else {
                v = '';
            }
            return v;
        },
        rotatorCallback: function(placement) {},
        jsonCallback: function(recs) {},
        js: function(){

                var scriptSrc = '',
                    placementsEmpty = false,
                    emptyPlacementName = '',
                    r3_pagetype;
                if (typeof r3_entity.placementTypes === this.U || r3_entity.placementTypes === '') {
                    placementsEmpty = true;
                }
                if (typeof r3_item !== this.U) {
                    emptyPlacementName = 'item_page';
                    r3_pagetype = r3_item;
                }
                if (typeof r3_category !== this.U) {
                    emptyPlacementName = 'category_page';
                    r3_pagetype = r3_category;
                }
                if (typeof r3_cart !== this.U) {
                    emptyPlacementName = 'cart_page';
                    r3_pagetype = r3_cart;
                }
                if (typeof r3_addtocart !== this.U) {
                    emptyPlacementName = 'add_to_cart_page';
                    r3_pagetype = r3_addtocart;
                }
                if (typeof r3_purchased !== this.U) {
                    emptyPlacementName = 'purchase_complete_page';
                    r3_pagetype = r3_purchased;
                }
                if (typeof r3_search !== this.U) {
                    emptyPlacementName = 'search_page';
                    r3_pagetype = r3_search;
                }
                if (typeof r3_dlp !== this.U) {
                    emptyPlacementName = 'dynamic_landing_page';
                    r3_pagetype = r3_dlp;
                }
                if (typeof r3_home !== this.U) {
                    emptyPlacementName = 'home_page';
                    r3_pagetype = r3_home;
                }
                if (typeof r3_error !== this.U) {
                    emptyPlacementName = 'error_page';
                    r3_pagetype = r3_error;
                }
                if (typeof r3_myrecs !== this.U) {
                    emptyPlacementName = 'my_recs_page';
                    r3_pagetype = r3_myrecs;
                }
                if (typeof r3_wishlist !== this.U) {
                    emptyPlacementName = 'cart_page';
                    r3_pagetype = r3_wishlist;
                }
                if (typeof r3_generic !== this.U) {
                    emptyPlacementName = 'generic_page';
                    r3_pagetype = r3_generic;
                }
                if (typeof r3_landing !== this.U) {
                    emptyPlacementName = 'landing_page';
                    r3_pagetype = r3_landing;
                }
                if (typeof r3_personal !== this.U) {
                    emptyPlacementName = 'personal_page';
                    r3_pagetype = r3_personal;
                }
                if (typeof r3_merchandised !== this.U) {
                    emptyPlacementName = 'merchandised_page';
                    r3_pagetype = r3_merchandised;
                }
                if (typeof r3_ensemble != this.U) {
                    emptyPlacementName = 'ensemble_page';
                    r3_pagetype = r3_ensemble;
                }
                if (typeof r3_registry !== this.U) {
                    emptyPlacementName = 'registry_page';
                    r3_pagetype = r3_registry;
                }
                if (typeof r3_addtoregistry !== this.U) {
                    emptyPlacementName = 'add_to_registry_page';
                    r3_pagetype = r3_addtoregistry;
                }
                if (typeof r3_brand !== this.U) {
                    emptyPlacementName = 'brand_page';
                    r3_pagetype = r3_brand;
                }

                if (r3_pagetype) {
                    var r3_pt = new r3_pagetype(this);
                    scriptSrc = r3_pt.createScript(scriptSrc);
                }
                scriptSrc = r3_entity.createScript(this, scriptSrc, placementsEmpty, emptyPlacementName);
                return scriptSrc;

        },
        log: function(eventData, commonData) {
            var imageSrc = '',
                prop, propValue, internalProp;
            if (commonData) {
                imageSrc = commonData.addCoreParams(imageSrc, 'log');
            } else {
                var d = new Date();
                imageSrc = eventData.baseUrl + path + '?a=' + encodeURIComponent(eventData.apiKey) + '&ts=' + d.getTime() + ((eventData.baseUrl.toLowerCase().indexOf('https://') === 0) ? '&ssl=t' : '') + imageSrc;
                delete eventData.baseUrl;
                delete eventData.apiKey;
                if (eventData.placementTypes) {
                    imageSrc += '&pt=' + encodeURIComponent(eventData.placementTypes);
                    delete eventData.placementTypes;
                }
                if (eventData.userId) {
                    imageSrc += '&u=' + encodeURIComponent(eventData.userId);
                    delete eventData.userId;
                }
                if (eventData.sessionId) {
                    imageSrc += '&s=' + encodeURIComponent(eventData.sessionId);
                    delete eventData.sessionId;
                }
                if (eventData.viewGuid && eventData.viewGuid !== '') {
                    imageSrc += '&vg=' + encodeURIComponent(eventData.viewGuid);
                    delete eventData.viewGuid;
                }
                if (eventData.segments) {
                    imageSrc += '&sgs=' + encodeURIComponent(eventData.segments);
                    delete eventData.segments;
                }
                if (eventData.channel) {
                    imageSrc += '&channelId=' + encodeURIComponent(eventData.channel);
                    delete eventData.channel;
                }
            }
            for (prop in eventData) {
                propValue = eventData[prop];
                imageSrc += '&' + prop + '=';
                if (_isArray(propValue)) {
                    imageSrc += encodeURIComponent(propValue.join('|'));
                } else if (propValue === Object(propValue)) {
                    var value = '';
                    for (internalProp in propValue) {
                        value += '|' + internalProp + ':';
                        if (_isArray(propValue[internalProp])) {
                            value += propValue[internalProp].join(';');
                        } else {
                            value += propValue[internalProp];
                        }
                    }
                    imageSrc += encodeURIComponent(value);
                } else {
                    imageSrc += encodeURIComponent(propValue);
                }
            }
            beacon(imageSrc);
        }
    }
};

function r3_common(RR_entity) {
    var self = this,
        internal = {},
        _isArray = function (obj) {
            return Object.prototype.toString.call(obj) == '[object Array]';
        },
        _richSortParams = {
            startRow: -1,
            count: -1,
            priceRanges: [],
            filterAttributes: {}
        },
        _innerAddContext = function (context, reset) {
            var prop, propValue, innerProp;
            if (typeof internal.context == RR_entity.U || reset) {
                internal.context = {};
            }
            for (prop in context) {
                propValue = context[prop];
                if (internal.context[prop] === undefined) {
                    internal.context[prop] = propValue;
                } else if (internal.context[prop] === Object(internal.context[prop]) && propValue === Object(propValue)) {
                    for (innerProp in propValue) {
                        internal.context[prop][innerProp] = propValue[innerProp];
                    }
                } else {
                    var a = internal.context[prop],
                        b = propValue;
                    if (!_isArray(a)) {
                        a = [a];
                    }
                    if (!_isArray(propValue)) {
                        b = [propValue];
                    }
                    internal.context[prop] = a.concat(b);
                }
            }
        },
        _innerAddFilter = function (type, property, propertyValues) {
            var context = {};
            context[type] = {};
            context[type][property] = propertyValues;
            _innerAddContext(context);
        };
    self.baseUrl = 'http://recs.richrelevance.com/rrserver/';
    self.jsFileName = 'p13n_generated.js';
    self.setPageBrand = rr_setBrand;
    self.addCategoryHintId = function (id) {
        if (typeof self.categoryHintIds == RR_entity.U) {
            self.categoryHintIds = '';
        }
        self.categoryHintIds += '|' + RR_entity.fixCatId(id);
    };
    self.addClickthruParams = function (index, params) {
        if (typeof self.clickthruParams == RR_entity.U) {
            self.clickthruParams = '';
        }
        self.clickthruParams += '|' + encodeURIComponent(index) + ':' + encodeURIComponent(params);
    };
    self.addContext = _innerAddContext;
    self.addFilter = function (filterName) {
        if (typeof self.filters == RR_entity.U) {
            self.filters = '';
        }
        self.filters += '|' + filterName;
    };
    self.addFilterBrand = function (filterBrand) {
        if (typeof self.filterBrands == RR_entity.U) {
            self.filterBrands = '';
        }
        self.filterBrands += '|' + RR_entity.fixName(filterBrand);
    };
    self.addFilterCategory = function (filterCategory) {
        if (typeof self.filterCategories == RR_entity.U) {
            self.filterCategories = '';
        }
        self.filterCategories += '|' + RR_entity.fixCatId(filterCategory);
    };
    self.addForcedPoolItem = function () {
    };
    self.addForcedTemplate = function () {
    };
    self.addInclusiveFilter = function (dimension, property, propertyValues) {
        _innerAddFilter("f-" + dimension, property, propertyValues);
    };
    self.addExclusiveFilter = function (dimension, property, propertyValues) {
        _innerAddFilter("f-" + dimension, "~" + property, propertyValues);
    };
    self.addItemId = function (id, sku) {
        if (typeof self.itemIds == RR_entity.U) {
            self.itemIds = '';
        }
        if (typeof sku != RR_entity.U) {
            id = id + "~" + sku;
        }
        self.itemIds += '|' + RR_entity.fixId(id);
    };
    self.addItemIdToCart = function (id, sku) {
        if (typeof self.addedToCartItemIds == RR_entity.U) {
            self.addedToCartItemIds = '';
        }
        if (typeof sku != RR_entity.U) {
            id = id + "~" + sku;
        }
        self.addedToCartItemIds += '|' + RR_entity.fixId(id);
    };
    self.addPlacementType = function (placementType) {
        if (typeof self.placementTypes == RR_entity.U) {
            self.placementTypes = '';
        }
        self.placementTypes += '|' + placementType;
    };
    self.addPromoType = function (promoType) {
        self.addPlacementType(promoType);
    };
    self.addRefinement = function (name, value) {
        if (typeof self.refinements == RR_entity.U) {
            self.refinements = '';
        }
        self.refinements += '|' + name + ':' + value;
    };
    self.addSearchTerm = function (searchTerm) {
        if (typeof self.searchTerms == RR_entity.U) {
            self.searchTerms = '';
        }
        self.searchTerms += '|' + searchTerm;
    };
    self.addSegment = function (segmentId, segmentName) {
        if (typeof self.segments == RR_entity.U) {
            self.segments = '';
        }
        if (segmentName === undefined) {
            self.segments += '|' + segmentId;
        } else {
            self.segments += '|' + segmentId + ':' + segmentName;
        }
    };
    self.addStrategy = function (strategyName) {
        if (typeof self.forcedStrategies == RR_entity.U) {
            self.forcedStrategies = '';
        }
        self.forcedStrategies += '|' + strategyName;
    };
    self.addUID = function (uid) {
        if (typeof self.uids == RR_entity.U) {
            self.uids = '';
        }
        self.uids += '|' + uid;
    };
    self.enableJson = function () {
        self.jsonEnabled = 't';
    };
    self.forceImmediateCallback = function () {
        self.immediateCallbackForced = 't';
    };
    self.forceListenMode = function () {
        self.listenModeForced = 't';
    };
    self.forceDisplayMode = function () {
        self.displayModeForced = 't';
    };
    self.forceDevMode = function () {
        self.devModeForced = 't';
    };
    self.setApiKey = function (apiKey) {
        self.apiKey = apiKey;
    };
    self.setBaseUrl = function (baseUrl) {
        if ('http://media.richrelevance.com/rrserver/' == baseUrl) {
            baseUrl = 'http://recs.richrelevance.com/rrserver/';
        }
        if ('https://media.richrelevance.com/rrserver/' == baseUrl) {
            baseUrl = 'https://recs.richrelevance.com/rrserver/';
        }
        self.baseUrl = baseUrl;
    };
    self.setCartValue = function (value) {
        internal.cartValue = value;
    };
    self.setChannel = function (channel) {
        internal.channel = channel;
    };
    self.setClearancePage = function (clearancePage) {
        self.clearancePage = clearancePage;
    };
    self.setClickthruServer = function (clickthruServer) {
        self.clickthruServer = clickthruServer;
    };
    self.setFilterBrandsIncludeMatchingElements = function (filterBrandsInclude) {
        self.filterBrandsInclude = filterBrandsInclude;
    };
    self.setFilterCategoriesIncludeMatchingElements = function (filterCategoriesInclude) {
        self.filterCategoriesInclude = filterCategoriesInclude;
    };
    self.setFilterPriceCentsMax = function (filterPriceCentsMax) {
        self.filterPriceCentsMax = filterPriceCentsMax;
    };
    self.setFilterPriceCentsMin = function (filterPriceCentsMin) {
        self.filterPriceCentsMin = filterPriceCentsMin;
    };
    self.setFilterPriceIncludeMatchingElements = function (filterPriceInclude) {
        self.filterPriceInclude = filterPriceInclude;
    };
    self.setFilterPriceMax = function (filterPriceMax) {
        self.filterPriceMax = filterPriceMax;
    };
    self.setFilterPriceMin = function (filterPriceMin) {
        self.filterPriceMin = filterPriceMin;
    };
    self.setForcedCampaign = function (campaign) {
        self.forcedCampaign = campaign;
    };
    self.showNoAds = function () {
        if (typeof self.forcedCampaign == RR_entity.U) {
            self.forcedCampaign = '0';
        }
    };
    self.setIpOverride = function (ipOverride) {
        self.ipOverride = ipOverride;
    };
    self.setForcedTreatment = function (treatment) {
        self.forcedTreatment = treatment;
    };
    self.setImageServer = function (imageServer) {
        self.imageServer = imageServer;
    };
    self.setJsFileName = function (jsFileName) {
        self.jsFileName = jsFileName;
    };
    self.setJsonCallback = function (jsonCallback) {
        self.jsonCallback = jsonCallback;
    };
    self.setJsPromoFileName = function (jsFileName) {
    };
    self.setLocale = function (locale) {
        self.locale = locale;
    };
    self.setRegionId = function (regionId) {
        self.regionId = regionId;
        if (self.apiKey == RR_entity.D) {
            internal.channel = regionId;
        }
        if (RR_entity.TM.indexOf("|" + self.apiKey + "|") > -1) {
            self.segments = '|' + regionId + ':' + regionId;
        }
    };
    self.setRegistryId = function (registryId) {
        self.registryId = registryId;
    };
    self.setRegistryType = function (registryType) {
        self.registryType = registryType;
    };
    self.setSessionId = function (sessionId) {
        self.sessionId = sessionId;
    };
    self.setUserId = function (userId) {
        self.userId = userId;
    };
    self.useDummyData = function () {
        self.dummyDataUsed = 't';
        self.displayModeForced = 't';
    };
    self.blockItemId = function (id) {
        if (typeof self.blockeditemIds == RR_entity.U) {
            self.blockeditemIds = '';
        }
        self.blockeditemIds += '|' + RR_entity.fixId(id);
    };
    self.RICHSORT = {
        paginate: function (startRow, count) {
            _richSortParams.startRow = startRow;
            _richSortParams.count = count;
        },
        filterPrice: function (priceRanges) {
            _richSortParams.priceRanges = priceRanges || [];
        },
        removeProducts: function (productIds) {
            var index = 0,
                len = productIds ? productIds.length : 0;
            for (; index < len; index += 1) {
                self.blockItemId(productIds[index]);
            }
        },
        filterAttribute: function (attributeName, attributeValues) {
            _richSortParams.filterAttributes[attributeName] = attributeValues;
        }
    };
    self.initFromParams = function (RR_entity) {
        if (RR_entity.lc('r3_forceDisplay=true')) {
            self.debugMode = true;
            self.displayModeForced = 't';
        }
        if (RR_entity.lc('r3_forceDev=true')) {
            self.debugMode = true;
            self.devModeForced = 't';
        }
        if (RR_entity.lc('r3_rad=true')) {
            self.debugMode = true;
            self.devModeForced = 't';
            self.rad = true;
            var radLevel = RR_entity.pq('r3_radLevel');
            if (radLevel !== '') {
                self.radLevel = radLevel;
            }
        }
        if (RR_entity.lc('r3_useDummyData=true')) {
            self.debugMode = true;
            self.dummyDataUsed = 't';
            self.displayModeForced = 't';
        }
        var tempForcedTreatment = RR_entity.pq('r3_forcedTreatment');
        if (tempForcedTreatment && tempForcedTreatment != '') {
            self.forcedTreatment = tempForcedTreatment;
        }
        var tempForcedCampaign = RR_entity.pq('r3_forcedCampaign');
        if (tempForcedCampaign && tempForcedCampaign != '') {
            self.forcedCampaign = tempForcedCampaign;
        }
        tempForcedCampaign = RR_entity.pq('r3_fc');
        if (tempForcedCampaign && tempForcedCampaign != '') {
            self.forcedCampaign = tempForcedCampaign;
        }
        var tempOverriddenIp = RR_entity.pq('r3_ipOverride');
        if (tempOverriddenIp && tempOverriddenIp != '') {
            self.ipOverride = tempOverriddenIp;
        }
        var tempForcedFtp = RR_entity.pq('r3_ftp');
        if (tempForcedFtp && tempForcedFtp != '') {
            self.forcedFtp = tempForcedFtp;
        }
        var tempRap = RR_entity.pq('r3_responseDetails');
        if (tempRap && tempRap != '') {
            self.rap = tempRap;
        }
        if (RR_entity.lc('r3_debugMode=true')) {
            self.debugMode = true;
        } else if (RR_entity.lc('r3_debugMode=false')) {
            self.debugMode = false;
        }
        if (RR_entity.lc('rr_vg=')) {
            self.viewGuid = RR_entity.pq('rr_vg');
        }
        if (typeof self.viewGuid == RR_entity.U && RR_entity.lc('vg=')) {
            self.viewGuid = RR_entity.pq('vg');
        }
        if (RR_entity.lc('rm=')) {
            self.fromRichMail = RR_entity.pq('rm');
        }
        if (RR_entity.lc('rr_u=')) {
            self.userId = RR_entity.pq('rr_u');
        }
        if (RR_entity.lc('rr_pcam=')) {
            self.promoCampaignId = RR_entity.pq('rr_pcam');
        }
        if (RR_entity.lc('rr_pcre=')) {
            self.promoCreativeId = RR_entity.pq('rr_pcre');
        }
        if (RR_entity.lc('rr_propt=')) {
            self.promoPlacementType = RR_entity.pq('rr_propt');
        }
        if (RR_entity.lc('rr_spoof=')) {
            self.spoof = RR_entity.pq('rr_spoof');
        }
        if (RR_entity.lc('rr_lpid=')) {
            self.landingPageId = RR_entity.pq('rr_lpid');
        }
    };
    self.addCoreParams = function (scriptSrc, path) {
        var d = new Date();
        scriptSrc = self.baseUrl + path + '?a=' + encodeURIComponent(self.apiKey) + '&ts=' + d.getTime() + ((self.baseUrl.toLowerCase().indexOf('https://') === 0) ? '&ssl=t' : '') + scriptSrc;
        if (self.placementTypes) {
            scriptSrc += '&pt=' + encodeURIComponent(self.placementTypes);
        }
        if (self.userId) {
            scriptSrc += '&u=' + encodeURIComponent(self.userId);
        }
        if (self.sessionId) {
            scriptSrc += '&s=' + encodeURIComponent(self.sessionId);
        }
        if (self.viewGuid && self.viewGuid !== '') {
            scriptSrc += '&vg=' + encodeURIComponent(self.viewGuid);
        }
        if (self.segments) {
            scriptSrc += '&sgs=' + encodeURIComponent(self.segments);
        }
        if (internal.channel) {
            scriptSrc += '&channelId=' + encodeURIComponent(internal.channel);
        }
        return scriptSrc;
    };
    this.createScript = function (RR_entity, scriptSrc, placementsEmpty, emptyPlacementName) {
        this.initFromParams(RR_entity);
        var prop, propValue, values, value, internalProp, attributeFilters = [],
            priceRanges = [],
            priceRangeIndex = 0,
            priceRangeLength, attribute;
        if (placementsEmpty) {
            this.addPlacementType(emptyPlacementName);
        }
        scriptSrc = this.addCoreParams(scriptSrc, self.jsFileName);
        scriptSrc += (placementsEmpty && (this.apiKey !== '7f65ff91442c1eae' && self.apiKey !== '5387d7af823640a7' && self.apiKey !== RR_entity.TD && self.apiKey !== '88ac00e4f3e16e44') ? '&pte=t' : '');
        if (self.clickthruServer) {
            scriptSrc += '&cts=' + encodeURIComponent(self.clickthruServer);
        }
        if (self.imageServer) {
            scriptSrc += '&imgsrv=' + encodeURIComponent(self.imageServer);
        }
        if (self.jsonEnabled && self.jsonEnabled == 't') {
            scriptSrc += '&je=t';
        }
        if (typeof self.landingPageId != RR_entity.U) {
            scriptSrc += '&lpid=' + self.landingPageId;
        }
        if (self.addedToCartItemIds) {
            scriptSrc += '&atcid=' + encodeURIComponent(self.addedToCartItemIds);
        }
        if (internal.cartValue) {
            scriptSrc += '&cv=' + encodeURIComponent(internal.cartValue);
        }
        if (self.forcedStrategies) {
            scriptSrc += '&fs=' + encodeURIComponent(self.forcedStrategies);
        }
        if (self.listenModeForced && self.listenModeForced == 't') {
            scriptSrc += '&flm=t';
        }
        if (self.forcedTreatment && self.forcedTreatment !== '') {
            scriptSrc += '&ftr=' + encodeURIComponent(self.forcedTreatment);
        }
        if (typeof self.forcedCampaign != RR_entity.U && self.forcedCampaign != '') {
            scriptSrc += '&fcmpn=' + encodeURIComponent(self.forcedCampaign);
        }
        if (typeof self.ipOverride != RR_entity.U && self.ipOverride != '') {
            scriptSrc += '&ipor=' + encodeURIComponent(self.ipOverride);
        }
        if (self.forcedFtp && self.forcedFtp != '') {
            scriptSrc += '&ftp=' + encodeURIComponent(self.forcedFtp);
        }
        if (self.rap && self.rap != '') {
            scriptSrc += '&rap=' + encodeURIComponent(self.rap);
        }
        if (self.fromRichMail && self.fromRichMail != '') {
            scriptSrc += '&rm=' + encodeURIComponent(self.fromRichMail);
        }
        if (self.categoryHintIds) {
            scriptSrc += '&chi=' + encodeURIComponent(self.categoryHintIds);
        }
        if (self.locale) {
            scriptSrc += '&flo=' + encodeURIComponent(self.locale);
        }
        if (self.brand) {
            scriptSrc += '&fpb=' + encodeURIComponent(self.brand);
        }
        if (typeof self.uids != RR_entity.U) {
            scriptSrc += '&uid=' + encodeURIComponent(self.uids);
        }
        if (typeof self.clearancePage != RR_entity.U) {
            scriptSrc += '&clp=' + encodeURIComponent(self.clearancePage);
        }
        if (self.filterBrands) {
            scriptSrc += '&filbr=' + encodeURIComponent(self.filterBrands);
        }
        if (self.filterBrandsInclude) {
            scriptSrc += '&filbrinc=' + encodeURIComponent(self.filterBrandsInclude);
        }
        if (self.filterCategories) {
            scriptSrc += '&filcat=' + encodeURIComponent(self.filterCategories);
        }
        if (self.filterCategoriesInclude) {
            scriptSrc += '&filcatinc=' + encodeURIComponent(self.filterCategoriesInclude);
        }
        if (self.filterPriceCentsMin) {
            scriptSrc += '&filprcmin=' + encodeURIComponent(self.filterPriceCentsMin);
        }
        if (self.filterPriceCentsMax) {
            scriptSrc += '&filprcmax=' + encodeURIComponent(self.filterPriceCentsMax);
        }
        if (self.filterPriceMin) {
            scriptSrc += '&filprmin=' + encodeURIComponent(self.filterPriceMin);
        }
        if (self.filterPriceMax) {
            scriptSrc += '&filprmax=' + encodeURIComponent(self.filterPriceMax);
        }
        if (self.filterPriceInclude) {
            scriptSrc += '&filprinc=' + encodeURIComponent(self.filterPriceInclude);
        }
        if (self.clickthruParams) {
            scriptSrc += '&ctp=' + encodeURIComponent(self.clickthruParams);
        }
        if (self.regionId) {
            scriptSrc += '&rid=' + encodeURIComponent(self.regionId);
        }
        if (self.filters) {
            scriptSrc += '&if=' + encodeURIComponent(self.filters);
        }
        if (self.refinements) {
            scriptSrc += '&rfm=' + encodeURIComponent(self.refinements);
        }
        if (typeof self.rad != RR_entity.U) {
            scriptSrc += '&rad=t';
        }
        if (typeof self.radLevel != RR_entity.U) {
            scriptSrc += '&radl=' + encodeURIComponent(self.radLevel);
        }
        if (typeof self.promoCampaignId != RR_entity.U) {
            scriptSrc += '&pcam=' + encodeURIComponent(self.promoCampaignId);
        }
        if (typeof self.promoCreativeId != RR_entity.U) {
            scriptSrc += '&pcre=' + encodeURIComponent(self.promoCreativeId);
        }
        if (typeof self.promoPlacementType != RR_entity.U) {
            scriptSrc += '&propt=' + encodeURIComponent(self.promoPlacementType);
        }
        if (typeof self.spoof != RR_entity.U) {
            scriptSrc += '&spoof=' + self.spoof;
        }
        if (typeof internal.context != RR_entity.U) {
            for (prop in internal.context) {
                propValue = internal.context[prop];
                scriptSrc += '&' + prop + '=';
                if (_isArray(propValue)) {
                    scriptSrc += encodeURIComponent(propValue.join('|'));
                } else if (propValue === Object(propValue)) {
                    values = [];
                    value = '';
                    for (internalProp in propValue) {
                        value = internalProp + ':';
                        if (_isArray(propValue[internalProp])) {
                            value += propValue[internalProp].join(';');
                        } else {
                            value += propValue[internalProp];
                        }
                        values.push(value);
                    }
                    scriptSrc += encodeURIComponent(values.join('|'));
                } else {
                    scriptSrc += encodeURIComponent(propValue);
                }
            }
        }
        if (self.registryId) {
            scriptSrc += '&rg=' + encodeURIComponent(self.registryId);
        }
        if (self.registryType) {
            scriptSrc += '&rgt=' + encodeURIComponent(self.registryType);
        }
        if (typeof self.searchTerms != RR_entity.U) {
            scriptSrc += '&st=' + encodeURIComponent(self.searchTerms);
        }
        if (self.jsonCallback) {
            scriptSrc += '&jcb=' + encodeURIComponent(self.jsonCallback);
        }
        if (self.immediateCallbackForced) {
            scriptSrc += '&icf=t';
        }
        if (self.blockeditemIds) {
            scriptSrc += '&bi=' + encodeURIComponent(self.blockeditemIds);
        }
        if (self.itemIds) {
            scriptSrc += '&p=' + encodeURIComponent(self.itemIds);
        }
        if (_richSortParams.startRow > 0) {
            scriptSrc += '&rssr=' + encodeURIComponent(_richSortParams.startRow);
        }
        if (_richSortParams.count > 0) {
            scriptSrc += '&rsrc=' + encodeURIComponent(_richSortParams.count);
        }
        if (typeof _richSortParams.priceRanges !== 'undefined' && _richSortParams.priceRanges.length > 0) {
            priceRangeLength = _richSortParams.priceRanges.length;
            for (; priceRangeIndex < priceRangeLength; priceRangeIndex = priceRangeIndex + 1) {
                priceRanges.push(_richSortParams.priceRanges[priceRangeIndex].join(';'));
            }
            scriptSrc += '&rspr=' + encodeURIComponent(priceRanges.join('|'));
        }
        for (attribute in _richSortParams.filterAttributes) {
            attributeFilters.push(attribute + ':' + _richSortParams.filterAttributes[attribute].join(';'));
        }
        if (attributeFilters.length > 0) {
            scriptSrc += '&rsfoa=' + encodeURIComponent(attributeFilters.join('|'));
        }
        if (self.debugMode) {
            if (self.displayModeForced && self.displayModeForced == 't') {
                scriptSrc += '&fdm=t';
            }
            if (self.devModeForced && self.devModeForced == 't') {
                scriptSrc += '&dev=t';
            }
            if (self.dummyDataUsed && self.dummyDataUsed == 't') {
                scriptSrc += '&udd=t';
            }
        }
        scriptSrc += '&l=1';
        return scriptSrc;
    }
}

function r3_item(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.blockItemId = r3_entity.blockItemId;
    self.setBrand = rr_setBrand;
    self.setId = rr_setId;
    self.setName = rr_setName;
    self.setTopLevelGenre = rr_setTopLevelGenre;
    self.addAttribute = function(name, value) {
        if (typeof self.attributes == RR_entity.U) {
            self.attributes = '';
        }
        self.attributes += '|' + name + ':' + value;
    };
    self.addCategory = rr_addCategory;
    self.addCategoryId = rr_addCategoryId;
    self.setCents = function(cents) {
        self.cents = cents;
    };
    self.setDescription = function(description) {
        self.description = description;
    };
    self.setDollarsAndCents = function(dollarsAndCents) {
        self.dollarsAndCents = dollarsAndCents;
    };
    self.setEndDate = function(endDate) {
        self.endDate = endDate;
    };
    self.setImageId = function(imageId) {
        self.imageId = imageId;
    };
    self.setInStock = function(inStock) {
        self.inStock = inStock;
    };
    self.setLinkId = function(linkId) {
        self.linkId = linkId;
    };
    self.setPrice = function(price) {
        self.price = price;
    };
    self.setRating = function(rating) {
        self.rating = rating;
    };
    self.setReleaseDate = function(releaseDate) {
        self.releaseDate = releaseDate;
    };
    self.setRecommendable = rr_setRecommendable;
    self.setSaleCents = function(saleCents) {
        self.saleCents = saleCents;
    };
    self.setSaleDollarsAndCents = function(saleDollarsAndCents) {
        self.saleDollarsAndCents = saleDollarsAndCents;
    };
    self.setSalePrice = function(salePrice) {
        self.salePrice = salePrice;
    };
    self.createScript = function(scriptSrc) {
        if (self.topLevelGenre) {
            scriptSrc += '&tg=' + encodeURIComponent(self.topLevelGenre);
        }
        if (self.categories) {
            scriptSrc += '&cs=' + encodeURIComponent(self.categories);
        }
        if (self.categoryIds) {
            scriptSrc += '&cis=' + encodeURIComponent(self.categoryIds);
        }
        if (typeof r3_entity.apiKey != RR_entity.U && r3_entity.apiKey == RR_entity.D && typeof r3_item != RR_entity.U && r3_entity.regionId == "us_04_en_bsd" && !self.id) {
            try {
                self.id = RR_entity.fixId(DELL.com.Delphi.PageSettings.mi.ProductCode);
            } catch (e) {}
        }
        if (self.id) {
            scriptSrc += '&p=' + encodeURIComponent(self.id);
        }
        if (self.name) {
            scriptSrc += '&n=' + encodeURIComponent(self.name);
        }
        if (self.description) {
            scriptSrc += '&d=' + encodeURIComponent(self.description);
        }
        if (self.imageId) {
            scriptSrc += '&ii=' + encodeURIComponent(self.imageId);
        }
        if (self.linkId) {
            scriptSrc += '&li=' + encodeURIComponent(self.linkId);
        }
        if (self.releaseDate) {
            scriptSrc += '&rd=' + encodeURIComponent(self.releaseDate);
        }
        if (self.dollarsAndCents) {
            scriptSrc += '&np=' + encodeURIComponent(self.dollarsAndCents);
        }
        if (self.cents) {
            scriptSrc += '&npc=' + encodeURIComponent(self.cents);
        }
        if (self.saleDollarsAndCents) {
            scriptSrc += '&sp=' + encodeURIComponent(self.saleDollarsAndCents);
        }
        if (self.saleCents) {
            scriptSrc += '&spc=' + encodeURIComponent(self.saleCents);
        }
        if (self.price) {
            scriptSrc += '&np=' + encodeURIComponent(self.price);
        }
        if (self.salePrice) {
            scriptSrc += '&sp=' + encodeURIComponent(self.salePrice);
        }
        if (self.endDate) {
            scriptSrc += '&ed=' + encodeURIComponent(self.endDate);
        }
        if (self.rating) {
            scriptSrc += '&r=' + encodeURIComponent(self.rating);
        }
        if (typeof self.recommendable != RR_entity.U) {
            scriptSrc += '&re=' + encodeURIComponent(self.recommendable);
        }
        if (self.brand) {
            scriptSrc += '&b=' + encodeURIComponent(self.brand);
        }
        if (self.attributes) {
            scriptSrc += '&at=' + encodeURIComponent(self.attributes);
        }
        if (typeof self.inStock != RR_entity.U) {
            scriptSrc += '&ins=' + encodeURIComponent(self.inStock);
        }
        return scriptSrc;
    }
}

function r3_category(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.addItemId = r3_entity.addItemId;
    self.setBrand = rr_setBrand;
    self.setId = rr_setId;
    self.setName = rr_setName;
    self.setTopLevelGenre = rr_setTopLevelGenre;
    self.setParentId = function(parentId) {
        self.parentId = RR_entity.fixCatId(parentId);
    };
    self.setTopName = function(topName) {
        self.topName = topName;
    };
    self.createScript = function(scriptSrc) {
        if (self.topLevelGenre) {
            scriptSrc += '&tg=' + encodeURIComponent(self.topLevelGenre);
        }
        if (self.name) {
            if (typeof r3_entity.apiKey != RR_entity.U && r3_entity.apiKey == RR_entity.D) {
                try {
                    self.id = RR_entity.fixCatId(self.name);
                } catch (e) {}
            } else {
                scriptSrc += '&cn=' + encodeURIComponent(self.name);
            }
        }
        if (self.id) {
            scriptSrc += '&c=' + encodeURIComponent(self.id);
        }
        if (self.parentId) {
            scriptSrc += '&pc=' + encodeURIComponent(self.parentId);
        }
        if (self.topName) {
            scriptSrc += '&tcn=' + encodeURIComponent(self.topName);
        }
        if (self.brand) {
            scriptSrc += '&b=' + encodeURIComponent(self.brand);
        }
        return scriptSrc;
    }
}

function r3_cart(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.addItemId = r3_entity.addItemId;
    self.addItemIdCentsQuantity = rr_addItemIdCentsQuantity;
    self.addItemIdDollarsAndCentsQuantity = rr_addItemIdDollarsAndCentsQuantity;
    self.addItemIdPriceQuantity = rr_addItemIdPriceQuantity;
    self.createScript = function(scriptSrc) {
        if (self.purchasesCents) {
            scriptSrc += '&ppc=' + encodeURIComponent(self.purchasesCents);
        }
        if (self.purchasesDollarsAndCents) {
            scriptSrc += '&pp=' + encodeURIComponent(self.purchasesDollarsAndCents);
        }
        if (self.quantities) {
            scriptSrc += '&q=' + encodeURIComponent(self.quantities);
        }
        if (self.purchasesPrice) {
            scriptSrc += '&pp=' + encodeURIComponent(self.purchasesPrice);
        }
        return scriptSrc;
    }
}

function r3_addtocart(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.addItemIdToCart = r3_entity.addItemIdToCart;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_purchased(RR_entity) {
    var self = this;
    self.addItemId = rr_addItemIdCentsQuantity;
    self.addItemIdCentsQuantity = rr_addItemIdCentsQuantity;
    self.addItemIdDollarsAndCentsQuantity = rr_addItemIdDollarsAndCentsQuantity;
    self.addItemIdPriceQuantity = rr_addItemIdPriceQuantity;
    self.setOrderNumber = function(orderNumber) {
        self.orderNumber = orderNumber;
    };
    self.createScript = function(scriptSrc) {
        if (self.orderNumber) {
            scriptSrc += '&o=' + encodeURIComponent(self.orderNumber);
        }
        if (self.purchasesCents) {
            scriptSrc += '&ppc=' + encodeURIComponent(self.purchasesCents);
        }
        if (self.purchasesDollarsAndCents) {
            scriptSrc += '&pp=' + encodeURIComponent(self.purchasesDollarsAndCents);
        }
        if (self.quantities) {
            scriptSrc += '&q=' + encodeURIComponent(self.quantities);
        }
        if (self.purchasesPrice) {
            scriptSrc += '&pp=' + encodeURIComponent(self.purchasesPrice);
        }
        return scriptSrc;
    }
}

function r3_search(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.addItemId = r3_entity.addItemId;
    self.setBrand = rr_setBrand;
    self.setTerms = r3_entity.addSearchTerm;
    self.createScript = function(scriptSrc) {
        if (self.brand) {
            scriptSrc += '&b=' + encodeURIComponent(self.brand);
        }
        return scriptSrc;
    }
}

function r3_home(RR_entity) {
    var self = this;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_dlp(RR_entity) {
    var self = this;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_error(RR_entity) {
    var self = this;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_myrecs(RR_entity) {
    var self = this;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_personal(RR_entity) {
    var self = this;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_merchandised(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.addItemId = r3_entity.addItemId;
    self.setName = rr_setName;
    self.createScript = function(scriptSrc) {
        if (self.name) {
            scriptSrc += '&n=' + encodeURIComponent(self.name);
        }
        return scriptSrc;
    }
}

function r3_wishlist(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.addItemId = r3_entity.addItemId;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_generic(RR_entity) {
    var self = this;
    self.setPageTypeId = rr_setPageTypeId;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_landing(RR_entity) {
    var self = this;
    self.isValid = function() {
        return true;
    };
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_ensemble(RR_entity) {
    var self = this;
    self.addCategoryId = rr_addCategoryId;
    self.setId = rr_setId;
    self.setRecommendable = rr_setRecommendable;
    self.createScript = function(scriptSrc) {
        if (self.categoryIds) {
            scriptSrc += '&cis=' + encodeURIComponent(self.categoryIds);
        }
        if (self.id) {
            scriptSrc += '&p=' + encodeURIComponent(self.id);
        }
        if (typeof self.recommendable != RR_entity.U) {
            scriptSrc += '&re=' + encodeURIComponent(self.recommendable);
        }
        return scriptSrc;
    }
}

function r3_registry(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.setRegistryId = r3_entity.setRegistryId;
    self.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_addtoregistry(RR_entity) {
    var self = this;
    var r3_entity = r3_common(RR_entity);
    self.setRegistryId = r3_common.setRegistryId;
    self.addItemIdCentsQuantity = rr_addItemIdCentsQuantity;
    self.addItemIdDollarsAndCentsQuantity = rr_addItemIdDollarsAndCentsQuantity;
    self.addItemIdPriceQuantity = rr_addItemIdPriceQuantity;
    self.addAlreadyAddedItemId = function(id) {
        if (typeof self.alreadyAddedRegistryItemIds == RR_entity.U) {
            self.alreadyAddedRegistryItemIds = '';
        }
        self.alreadyAddedRegistryItemIds += '|' + id;
    };
    self.createScript = function(scriptSrc) {
        if (self.alreadyAddedRegistryItemIds) {
            scriptSrc += '&aari=' + encodeURIComponent(self.alreadyAddedRegistryItemIds);
        } else if (r3_entity.itemIds) {
            scriptSrc += '&aari=' + encodeURIComponent(r3_entity.itemIds);
        }
        if (self.purchasesCents) {
            scriptSrc += '&ppc=' + encodeURIComponent(self.purchasesCents);
        }
        if (self.purchasesDollarsAndCents) {
            scriptSrc += '&pp=' + encodeURIComponent(self.purchasesDollarsAndCents);
        }
        if (self.purchasesPrice) {
            scriptSrc += '&pp=' + encodeURIComponent(self.purchasesPrice);
        }
        if (self.quantities) {
            scriptSrc += '&q=' + encodeURIComponent(self.quantities);
        }
        return scriptSrc;
    }
}

function r3_brand(RR_entity) {
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function rr_setBrand(brand) {
    this.brand = RR.fixName(brand);
}

function main(url, product_id){
    rr = new RR(url, product_id);
    return rr.js();
}