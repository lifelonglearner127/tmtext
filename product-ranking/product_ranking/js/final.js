debugger;

var RR = function(href, id) {
    var _isArray = function(obj) {
        return Object.prototype.toString.call(obj) == '[object Array]';
    };
    var r3_entity = new r3_common(this);
    var jsdom = require("jsdom");
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

                jsdom.env({
                    url: this.l,
                    src: ['http://code.jquery.com/jquery-1.5.min.js'],
                    done: function (errors, window) {

                        var RSobjs = window.jQuery("section.recordSpotlight.richRelevance:not(.RRdone)");
                            RSobjs.each(function(i){
                                r3_entity.addPlacementType("item_page.rr" + (i+1));
                            });
                            r3_entity.placementTypes = '-----------------'
                    },
                  features: {
                    FetchExternalResources: ["script"],
                    ProcessExternalResources: ["script"],
                    SkipExternalResources: false
                  }
                });




                if (typeof r3_entity.placementTypes === this.U || r3_entity.placementTypes === '') {
                    placementsEmpty = true;
                }
                if (typeof r3_item !== this.U) {
                    emptyPlacementName = 'item_page';
                    r3_pagetype = r3_item;
                }
                if (r3_pagetype) {
                    var r3_pt = new r3_pagetype(this);
                    scriptSrc = r3_pt.createScript(scriptSrc);
                }
                scriptSrc = r3_entity.createScript(this, scriptSrc, placementsEmpty, emptyPlacementName);
                return scriptSrc;
        }
    }
};

function rr_addCategory(id, name) {
    if (typeof this.categories == RR.U) {
        this.categories = '';
    }
    if (typeof name == RR.U) {
        name = id;
    }
    this.categories += '|' + RR.fixCatId(id) + ':' + name;
}

function rr_addCategoryId(id) {
    if (typeof this.categoryIds == RR.U) {
        this.categoryIds = '';
    }
    this.categoryIds += '|' + RR.fixCatId(id);
}

function rr_addItemIdCentsQuantity(id, cents, quantity, sku) {
    R3_COMMON.addItemId(id, sku);
    if (typeof this.purchasesCents == RR.U) {
        this.purchasesCents = '';
    }
    if (typeof cents == RR.U) {
        cents = 0;
    }
    this.purchasesCents += '|' + cents;
    if (typeof this.quantities == RR.U) {
        this.quantities = '';
    }
    if (typeof quantity == RR.U) {
        quantity = -1;
    }
    quantity = quantity + '';
    if (quantity.indexOf('.') != -1) {
        quantity = quantity.substring(0, quantity.indexOf('.'));
    }
    this.quantities += '|' + quantity;
}

function rr_addItemIdDollarsAndCentsQuantity(id, dollarsAndCents, quantity, sku) {
    R3_COMMON.addItemId(id, sku);
    if (typeof this.purchasesDollarsAndCents == RR.U) {
        this.purchasesDollarsAndCents = '';
    }
    if (typeof dollarsAndCents == RR.U) {
        dollarsAndCents = 0;
    }
    this.purchasesDollarsAndCents += '|' + dollarsAndCents;
    if (typeof this.quantities == RR.U) {
        this.quantities = '';
    }
    if (typeof quantity == RR.U) {
        quantity = -1;
    }
    quantity = quantity + '';
    if (quantity.indexOf('.') != -1) {
        quantity = quantity.substring(0, quantity.indexOf('.'));
    }
    this.quantities += '|' + quantity;
}

function rr_addItemIdPriceQuantity(id, price, quantity, sku) {
    R3_COMMON.addItemId(id, sku);
    if (typeof this.purchasesPrice == RR.U) {
        this.purchasesPrice = '';
    }
    if (typeof price == RR.U) {
        price = 0;
    }
    this.purchasesPrice += '|' + price;
    if (typeof this.quantities == RR.U) {
        this.quantities = '';
    }
    if (typeof quantity == RR.U) {
        quantity = -1;
    }
    quantity = quantity + '';
    if (quantity.indexOf('.') != -1) {
        quantity = quantity.substring(0, quantity.indexOf('.'));
    }
    this.quantities += '|' + quantity;
}

function rr_setBrand(brand) {
    this.brand = RR.fixName(brand);
}

function rr_setId(id) {
    this.id = RR.fixCatId(id);
}

function rr_setName(name) {
    this.name = name;
}

function rr_setRecommendable(recommendable) {
    this.recommendable = recommendable;
}

function rr_setTopLevelGenre(topLevelGenre) {
    this.topLevelGenre = topLevelGenre;
}

function rr_setPageTypeId(pageTypeId) {
    this.pageTypeId = pageTypeId;
}

function r3_common(RR_entity) {
    var internal = {},
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
    this.baseUrl = 'http://recs.richrelevance.com/rrserver/';
    this.jsFileName = 'p13n_generated.js';
    this.placementTypes = '';
    this.setPageBrand = rr_setBrand;
    this.addCategoryHintId = function (id) {
        if (typeof this.categoryHintIds == RR_entity.U) {
            this.categoryHintIds = '';
        }
        this.categoryHintIds += '|' + RR_entity.fixCatId(id);
    };
    this.addClickthruParams = function (index, params) {
        if (typeof this.clickthruParams == RR_entity.U) {
            this.clickthruParams = '';
        }
        this.clickthruParams += '|' + encodeURIComponent(index) + ':' + encodeURIComponent(params);
    };
    this.addContext = _innerAddContext;
    this.addFilter = function (filterName) {
        if (typeof this.filters == RR_entity.U) {
            this.filters = '';
        }
        this.filters += '|' + filterName;
    };
    this.addFilterBrand = function (filterBrand) {
        if (typeof this.filterBrands == RR_entity.U) {
            this.filterBrands = '';
        }
        this.filterBrands += '|' + RR_entity.fixName(filterBrand);
    };
    this.addFilterCategory = function (filterCategory) {
        if (typeof this.filterCategories == RR_entity.U) {
            this.filterCategories = '';
        }
        this.filterCategories += '|' + RR_entity.fixCatId(filterCategory);
    };
    this.addForcedPoolItem = function () {
    };
    this.addForcedTemplate = function () {
    };
    this.addInclusiveFilter = function (dimension, property, propertyValues) {
        _innerAddFilter("f-" + dimension, property, propertyValues);
    };
    this.addExclusiveFilter = function (dimension, property, propertyValues) {
        _innerAddFilter("f-" + dimension, "~" + property, propertyValues);
    };
    this.addItemId = function (id, sku) {
        if (typeof this.itemIds == RR_entity.U) {
            this.itemIds = '';
        }
        if (typeof sku != RR_entity.U) {
            id = id + "~" + sku;
        }
        this.itemIds += '|' + RR_entity.fixId(id);
    };
    this.addItemIdToCart = function (id, sku) {
        if (typeof this.addedToCartItemIds == RR_entity.U) {
            this.addedToCartItemIds = '';
        }
        if (typeof sku != RR_entity.U) {
            id = id + "~" + sku;
        }
        this.addedToCartItemIds += '|' + RR_entity.fixId(id);
    };
    this.addPlacementType = function (placementType) {
        if (typeof this.placementTypes == RR_entity.U) {
            this.placementTypes = '';
        }
        this.placementTypes += '|' + placementType;
    };
    this.addPromoType = function (promoType) {
        this.addPlacementType(promoType);
    };
    this.addRefinement = function (name, value) {
        if (typeof this.refinements == RR_entity.U) {
            this.refinements = '';
        }
        this.refinements += '|' + name + ':' + value;
    };
    this.addSearchTerm = function (searchTerm) {
        if (typeof this.searchTerms == RR_entity.U) {
            this.searchTerms = '';
        }
        this.searchTerms += '|' + searchTerm;
    };
    this.addSegment = function (segmentId, segmentName) {
        if (typeof this.segments == RR_entity.U) {
            this.segments = '';
        }
        if (segmentName === undefined) {
            this.segments += '|' + segmentId;
        } else {
            this.segments += '|' + segmentId + ':' + segmentName;
        }
    };
    this.addStrategy = function (strategyName) {
        if (typeof this.forcedStrategies == RR_entity.U) {
            this.forcedStrategies = '';
        }
        this.forcedStrategies += '|' + strategyName;
    };
    this.addUID = function (uid) {
        if (typeof this.uids == RR_entity.U) {
            this.uids = '';
        }
        this.uids += '|' + uid;
    };
    this.enableJson = function () {
        this.jsonEnabled = 't';
    };
    this.forceImmediateCallback = function () {
        this.immediateCallbackForced = 't';
    };
    this.forceListenMode = function () {
        this.listenModeForced = 't';
    };
    this.forceDisplayMode = function () {
        this.displayModeForced = 't';
    };
    this.forceDevMode = function () {
        this.devModeForced = 't';
    };
    this.setApiKey = function (apiKey) {
        this.apiKey = apiKey;
    };
    this.setBaseUrl = function (baseUrl) {
        if ('http://media.richrelevance.com/rrserver/' == baseUrl) {
            baseUrl = 'http://recs.richrelevance.com/rrserver/';
        }
        if ('https://media.richrelevance.com/rrserver/' == baseUrl) {
            baseUrl = 'https://recs.richrelevance.com/rrserver/';
        }
        this.baseUrl = baseUrl;
    };
    this.setCartValue = function (value) {
        internal.cartValue = value;
    };
    this.setChannel = function (channel) {
        internal.channel = channel;
    };
    this.setClearancePage = function (clearancePage) {
        this.clearancePage = clearancePage;
    };
    this.setClickthruServer = function (clickthruServer) {
        this.clickthruServer = clickthruServer;
    };
    this.setFilterBrandsIncludeMatchingElements = function (filterBrandsInclude) {
        this.filterBrandsInclude = filterBrandsInclude;
    };
    this.setFilterCategoriesIncludeMatchingElements = function (filterCategoriesInclude) {
        this.filterCategoriesInclude = filterCategoriesInclude;
    };
    this.setFilterPriceCentsMax = function (filterPriceCentsMax) {
        this.filterPriceCentsMax = filterPriceCentsMax;
    };
    this.setFilterPriceCentsMin = function (filterPriceCentsMin) {
        this.filterPriceCentsMin = filterPriceCentsMin;
    };
    this.setFilterPriceIncludeMatchingElements = function (filterPriceInclude) {
        this.filterPriceInclude = filterPriceInclude;
    };
    this.setFilterPriceMax = function (filterPriceMax) {
        this.filterPriceMax = filterPriceMax;
    };
    this.setFilterPriceMin = function (filterPriceMin) {
        this.filterPriceMin = filterPriceMin;
    };
    this.setForcedCampaign = function (campaign) {
        this.forcedCampaign = campaign;
    };
    this.showNoAds = function () {
        if (typeof this.forcedCampaign == RR_entity.U) {
            this.forcedCampaign = '0';
        }
    };
    this.setIpOverride = function (ipOverride) {
        this.ipOverride = ipOverride;
    };
    this.setForcedTreatment = function (treatment) {
        this.forcedTreatment = treatment;
    };
    this.setImageServer = function (imageServer) {
        this.imageServer = imageServer;
    };
    this.setJsFileName = function (jsFileName) {
        this.jsFileName = jsFileName;
    };
    this.setJsonCallback = function (jsonCallback) {
        this.jsonCallback = jsonCallback;
    };
    this.setJsPromoFileName = function (jsFileName) {
    };
    this.setLocale = function (locale) {
        this.locale = locale;
    };
    this.setRegionId = function (regionId) {
        this.regionId = regionId;
        if (this.apiKey == RR_entity.D) {
            internal.channel = regionId;
        }
        if (RR_entity.TM.indexOf("|" + this.apiKey + "|") > -1) {
            this.segments = '|' + regionId + ':' + regionId;
        }
    };
    this.setRegistryId = function (registryId) {
        this.registryId = registryId;
    };
    this.setRegistryType = function (registryType) {
        this.registryType = registryType;
    };
    this.setSessionId = function (sessionId) {
        this.sessionId = sessionId;
    };
    this.setUserId = function (userId) {
        this.userId = userId;
    };
    this.useDummyData = function () {
        this.dummyDataUsed = 't';
        this.displayModeForced = 't';
    };
    this.blockItemId = function (id) {
        if (typeof this.blockeditemIds == RR_entity.U) {
            this.blockeditemIds = '';
        }
        this.blockeditemIds += '|' + RR_entity.fixId(id);
    };
    this.RICHSORT = {
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
                this.blockItemId(productIds[index]);
            }
        },
        filterAttribute: function (attributeName, attributeValues) {
            _richSortParams.filterAttributes[attributeName] = attributeValues;
        }
    };
    this.initFromParams = function (RR_entity) {
        if (RR_entity.lc('r3_forceDisplay=true')) {
            this.debugMode = true;
            this.displayModeForced = 't';
        }
        if (RR_entity.lc('r3_forceDev=true')) {
            this.debugMode = true;
            this.devModeForced = 't';
        }
        if (RR_entity.lc('r3_rad=true')) {
            this.debugMode = true;
            this.devModeForced = 't';
            this.rad = true;
            var radLevel = RR_entity.pq('r3_radLevel');
            if (radLevel !== '') {
                this.radLevel = radLevel;
            }
        }
        if (RR_entity.lc('r3_useDummyData=true')) {
            this.debugMode = true;
            this.dummyDataUsed = 't';
            this.displayModeForced = 't';
        }
        var tempForcedTreatment = RR_entity.pq('r3_forcedTreatment');
        if (tempForcedTreatment && tempForcedTreatment != '') {
            this.forcedTreatment = tempForcedTreatment;
        }
        var tempForcedCampaign = RR_entity.pq('r3_forcedCampaign');
        if (tempForcedCampaign && tempForcedCampaign != '') {
            this.forcedCampaign = tempForcedCampaign;
        }
        tempForcedCampaign = RR_entity.pq('r3_fc');
        if (tempForcedCampaign && tempForcedCampaign != '') {
            this.forcedCampaign = tempForcedCampaign;
        }
        var tempOverriddenIp = RR_entity.pq('r3_ipOverride');
        if (tempOverriddenIp && tempOverriddenIp != '') {
            this.ipOverride = tempOverriddenIp;
        }
        var tempForcedFtp = RR_entity.pq('r3_ftp');
        if (tempForcedFtp && tempForcedFtp != '') {
            this.forcedFtp = tempForcedFtp;
        }
        var tempRap = RR_entity.pq('r3_responseDetails');
        if (tempRap && tempRap != '') {
            this.rap = tempRap;
        }
        if (RR_entity.lc('r3_debugMode=true')) {
            this.debugMode = true;
        } else if (RR_entity.lc('r3_debugMode=false')) {
            this.debugMode = false;
        }
        if (RR_entity.lc('rr_vg=')) {
            this.viewGuid = RR_entity.pq('rr_vg');
        }
        if (typeof this.viewGuid == RR_entity.U && RR_entity.lc('vg=')) {
            this.viewGuid = RR_entity.pq('vg');
        }
        if (RR_entity.lc('rm=')) {
            this.fromRichMail = RR_entity.pq('rm');
        }
        if (RR_entity.lc('rr_u=')) {
            this.userId = RR_entity.pq('rr_u');
        }
        if (RR_entity.lc('rr_pcam=')) {
            this.promoCampaignId = RR_entity.pq('rr_pcam');
        }
        if (RR_entity.lc('rr_pcre=')) {
            this.promoCreativeId = RR_entity.pq('rr_pcre');
        }
        if (RR_entity.lc('rr_propt=')) {
            this.promoPlacementType = RR_entity.pq('rr_propt');
        }
        if (RR_entity.lc('rr_spoof=')) {
            this.spoof = RR_entity.pq('rr_spoof');
        }
        if (RR_entity.lc('rr_lpid=')) {
            this.landingPageId = RR_entity.pq('rr_lpid');
        }
    };
    this.addCoreParams = function (scriptSrc, path) {
        var d = new Date();
        this.setApiKey('45c4b1787d30a004');
        scriptSrc = this.baseUrl + path + '?a=' + encodeURIComponent(this.apiKey) + '&ts=' + d.getTime() + ((this.baseUrl.toLowerCase().indexOf('https://') === 0) ? '&ssl=t' : '') + scriptSrc;
        if (this.placementTypes) {
            scriptSrc += '&pt=' + encodeURIComponent(this.placementTypes);
        }
        if (this.userId) {
            scriptSrc += '&u=' + encodeURIComponent(this.userId);
        }
        if (this.sessionId) {
            scriptSrc += '&s=' + encodeURIComponent(this.sessionId);
        }
        if (this.viewGuid && this.viewGuid !== '') {
            scriptSrc += '&vg=' + encodeURIComponent(this.viewGuid);
        }
        if (this.segments) {
            scriptSrc += '&sgs=' + encodeURIComponent(this.segments);
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
        scriptSrc = this.addCoreParams(scriptSrc, this.jsFileName);
        scriptSrc += (placementsEmpty && (this.apiKey !== '7f65ff91442c1eae' && this.apiKey !== '5387d7af823640a7' && this.apiKey !== RR_entity.TD && this.apiKey !== '88ac00e4f3e16e44') ? '&pte=t' : '');
        if (this.clickthruServer) {
            scriptSrc += '&cts=' + encodeURIComponent(this.clickthruServer);
        }
        if (this.imageServer) {
            scriptSrc += '&imgsrv=' + encodeURIComponent(this.imageServer);
        }
        if (this.jsonEnabled && this.jsonEnabled == 't') {
            scriptSrc += '&je=t';
        }
        if (typeof this.landingPageId != RR_entity.U) {
            scriptSrc += '&lpid=' + this.landingPageId;
        }
        if (this.addedToCartItemIds) {
            scriptSrc += '&atcid=' + encodeURIComponent(this.addedToCartItemIds);
        }
        if (internal.cartValue) {
            scriptSrc += '&cv=' + encodeURIComponent(internal.cartValue);
        }
        if (this.forcedStrategies) {
            scriptSrc += '&fs=' + encodeURIComponent(this.forcedStrategies);
        }
        if (this.listenModeForced && this.listenModeForced == 't') {
            scriptSrc += '&flm=t';
        }
        if (this.forcedTreatment && this.forcedTreatment !== '') {
            scriptSrc += '&ftr=' + encodeURIComponent(this.forcedTreatment);
        }
        if (typeof this.forcedCampaign != RR_entity.U && this.forcedCampaign != '') {
            scriptSrc += '&fcmpn=' + encodeURIComponent(this.forcedCampaign);
        }
        if (typeof this.ipOverride != RR_entity.U && this.ipOverride != '') {
            scriptSrc += '&ipor=' + encodeURIComponent(this.ipOverride);
        }
        if (this.forcedFtp && this.forcedFtp != '') {
            scriptSrc += '&ftp=' + encodeURIComponent(this.forcedFtp);
        }
        if (this.rap && this.rap != '') {
            scriptSrc += '&rap=' + encodeURIComponent(this.rap);
        }
        if (this.fromRichMail && this.fromRichMail != '') {
            scriptSrc += '&rm=' + encodeURIComponent(this.fromRichMail);
        }
        if (this.categoryHintIds) {
            scriptSrc += '&chi=' + encodeURIComponent(this.categoryHintIds);
        }
        if (this.locale) {
            scriptSrc += '&flo=' + encodeURIComponent(this.locale);
        }
        if (this.brand) {
            scriptSrc += '&fpb=' + encodeURIComponent(this.brand);
        }
        if (typeof this.uids != RR_entity.U) {
            scriptSrc += '&uid=' + encodeURIComponent(this.uids);
        }
        if (typeof this.clearancePage != RR_entity.U) {
            scriptSrc += '&clp=' + encodeURIComponent(this.clearancePage);
        }
        if (this.filterBrands) {
            scriptSrc += '&filbr=' + encodeURIComponent(this.filterBrands);
        }
        if (this.filterBrandsInclude) {
            scriptSrc += '&filbrinc=' + encodeURIComponent(this.filterBrandsInclude);
        }
        if (this.filterCategories) {
            scriptSrc += '&filcat=' + encodeURIComponent(this.filterCategories);
        }
        if (this.filterCategoriesInclude) {
            scriptSrc += '&filcatinc=' + encodeURIComponent(this.filterCategoriesInclude);
        }
        if (this.filterPriceCentsMin) {
            scriptSrc += '&filprcmin=' + encodeURIComponent(this.filterPriceCentsMin);
        }
        if (this.filterPriceCentsMax) {
            scriptSrc += '&filprcmax=' + encodeURIComponent(this.filterPriceCentsMax);
        }
        if (this.filterPriceMin) {
            scriptSrc += '&filprmin=' + encodeURIComponent(this.filterPriceMin);
        }
        if (this.filterPriceMax) {
            scriptSrc += '&filprmax=' + encodeURIComponent(this.filterPriceMax);
        }
        if (this.filterPriceInclude) {
            scriptSrc += '&filprinc=' + encodeURIComponent(this.filterPriceInclude);
        }
        if (this.clickthruParams) {
            scriptSrc += '&ctp=' + encodeURIComponent(this.clickthruParams);
        }
        if (this.regionId) {
            scriptSrc += '&rid=' + encodeURIComponent(this.regionId);
        }
        if (this.filters) {
            scriptSrc += '&if=' + encodeURIComponent(this.filters);
        }
        if (this.refinements) {
            scriptSrc += '&rfm=' + encodeURIComponent(this.refinements);
        }
        if (typeof this.rad != RR_entity.U) {
            scriptSrc += '&rad=t';
        }
        if (typeof this.radLevel != RR_entity.U) {
            scriptSrc += '&radl=' + encodeURIComponent(this.radLevel);
        }
        if (typeof this.promoCampaignId != RR_entity.U) {
            scriptSrc += '&pcam=' + encodeURIComponent(this.promoCampaignId);
        }
        if (typeof this.promoCreativeId != RR_entity.U) {
            scriptSrc += '&pcre=' + encodeURIComponent(this.promoCreativeId);
        }
        if (typeof this.promoPlacementType != RR_entity.U) {
            scriptSrc += '&propt=' + encodeURIComponent(this.promoPlacementType);
        }
        if (typeof this.spoof != RR_entity.U) {
            scriptSrc += '&spoof=' + this.spoof;
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
        if (this.registryId) {
            scriptSrc += '&rg=' + encodeURIComponent(this.registryId);
        }
        if (this.registryType) {
            scriptSrc += '&rgt=' + encodeURIComponent(this.registryType);
        }
        if (typeof this.searchTerms != RR_entity.U) {
            scriptSrc += '&st=' + encodeURIComponent(this.searchTerms);
        }
        if (this.jsonCallback) {
            scriptSrc += '&jcb=' + encodeURIComponent(this.jsonCallback);
        }
        if (this.immediateCallbackForced) {
            scriptSrc += '&icf=t';
        }
        if (this.blockeditemIds) {
            scriptSrc += '&bi=' + encodeURIComponent(this.blockeditemIds);
        }
        if (this.itemIds) {
            scriptSrc += '&p=' + encodeURIComponent(this.itemIds);
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
        if (this.debugMode) {
            if (this.displayModeForced && this.displayModeForced == 't') {
                scriptSrc += '&fdm=t';
            }
            if (this.devModeForced && this.devModeForced == 't') {
                scriptSrc += '&dev=t';
            }
            if (this.dummyDataUsed && this.dummyDataUsed == 't') {
                scriptSrc += '&udd=t';
            }
        }
        scriptSrc += '&l=1';
        return scriptSrc;
    }
}

function r3_item(RR_entity) {
    var r3_entity = new r3_common(RR_entity);
    this.blockItemId = r3_entity.blockItemId;
    this.id = RR_entity.id;
    this.setBrand = rr_setBrand;
    this.setId = rr_setId;
    this.setName = rr_setName;
    this.setTopLevelGenre = rr_setTopLevelGenre;
    this.addAttribute = function(name, value) {
        if (typeof this.attributes == RR.U) {
            this.attributes = ''
        }
        this.attributes += '|' + name + ':' + value
    };
    this.addCategory = rr_addCategory;
    this.addCategoryId = rr_addCategoryId;
    this.setCents = function(cents) {
        this.cents = cents
    };
    this.setDescription = function(description) {
        this.description = description
    };
    this.setDollarsAndCents = function(dollarsAndCents) {
        this.dollarsAndCents = dollarsAndCents
    };
    this.setEndDate = function(endDate) {
        this.endDate = endDate
    };
    this.setImageId = function(imageId) {
        this.imageId = imageId
    };
    this.setInStock = function(inStock) {
        this.inStock = inStock
    };
    this.setLinkId = function(linkId) {
        this.linkId = linkId
    };
    this.setPrice = function(price) {
        this.price = price
    };
    this.setRating = function(rating) {
        this.rating = rating
    };
    this.setReleaseDate = function(releaseDate) {
        this.releaseDate = releaseDate
    };
    this.setRecommendable = rr_setRecommendable;
    this.setSaleCents = function(saleCents) {
        this.saleCents = saleCents
    };
    this.setSaleDollarsAndCents = function(saleDollarsAndCents) {
        this.saleDollarsAndCents = saleDollarsAndCents
    };
    this.setSalePrice = function(salePrice) {
        this.salePrice = salePrice
    };
    this.createScript = function(scriptSrc) {
        if (this.topLevelGenre) {
            scriptSrc += '&tg=' + encodeURIComponent(this.topLevelGenre)
        }
        if (this.categories) {
            scriptSrc += '&cs=' + encodeURIComponent(this.categories)
        }
        if (this.categoryIds) {
            scriptSrc += '&cis=' + encodeURIComponent(this.categoryIds)
        }
        if (typeof r3_entity.apiKey != RR.U && r3_entity.apiKey == RR.D && typeof r3_item != RR_entity.U && r3_entity.regionId == "us_04_en_bsd" && !this.id) {
            try {
                this.id = RR.fixId(DELL.com.Delphi.PageSettings.mi.ProductCode)
            } catch (e) {}
        }
        if (this.id) {
            scriptSrc += '&p=' + encodeURIComponent(RR_entity.id)
        }
        if (this.name) {
            scriptSrc += '&n=' + encodeURIComponent(this.name)
        }
        if (this.description) {
            scriptSrc += '&d=' + encodeURIComponent(this.description)
        }
        if (this.imageId) {
            scriptSrc += '&ii=' + encodeURIComponent(this.imageId)
        }
        if (this.linkId) {
            scriptSrc += '&li=' + encodeURIComponent(this.linkId)
        }
        if (this.releaseDate) {
            scriptSrc += '&rd=' + encodeURIComponent(this.releaseDate)
        }
        if (this.dollarsAndCents) {
            scriptSrc += '&np=' + encodeURIComponent(this.dollarsAndCents)
        }
        if (this.cents) {
            scriptSrc += '&npc=' + encodeURIComponent(this.cents)
        }
        if (this.saleDollarsAndCents) {
            scriptSrc += '&sp=' + encodeURIComponent(this.saleDollarsAndCents)
        }
        if (this.saleCents) {
            scriptSrc += '&spc=' + encodeURIComponent(this.saleCents)
        }
        if (this.price) {
            scriptSrc += '&np=' + encodeURIComponent(this.price)
        }
        if (this.salePrice) {
            scriptSrc += '&sp=' + encodeURIComponent(this.salePrice)
        }
        if (this.endDate) {
            scriptSrc += '&ed=' + encodeURIComponent(this.endDate)
        }
        if (this.rating) {
            scriptSrc += '&r=' + encodeURIComponent(this.rating)
        }
        if (typeof this.recommendable != RR_entity.U) {
            scriptSrc += '&re=' + encodeURIComponent(this.recommendable)
        }
        if (this.brand) {
            scriptSrc += '&b=' + encodeURIComponent(this.brand)
        }
        if (this.attributes) {
            scriptSrc += '&at=' + encodeURIComponent(this.attributes)
        }
        if (typeof this.inStock != RR_entity.U) {
            scriptSrc += '&ins=' + encodeURIComponent(this.inStock)
        }
        return scriptSrc
    }
}

function r3_category(RR_entity) {
    var r3_entity = r3_common(RR_entity);
    this.addItemId = r3_entity.addItemId;
    this.setBrand = rr_setBrand;
    this.setId = rr_setId;
    this.setName = rr_setName;
    this.setTopLevelGenre = rr_setTopLevelGenre;
    this.setParentId = function(parentId) {
        this.parentId = RR_entity.fixCatId(parentId);
    };
    this.setTopName = function(topName) {
        this.topName = topName;
    };
    this.createScript = function(scriptSrc) {
        if (this.topLevelGenre) {
            scriptSrc += '&tg=' + encodeURIComponent(this.topLevelGenre);
        }
        if (this.name) {
            if (typeof r3_entity.apiKey != RR_entity.U && r3_entity.apiKey == RR_entity.D) {
                try {
                    this.id = RR_entity.fixCatId(this.name);
                } catch (e) {}
            } else {
                scriptSrc += '&cn=' + encodeURIComponent(this.name);
            }
        }
        if (this.id) {
            scriptSrc += '&c=' + encodeURIComponent(this.id);
        }
        if (this.parentId) {
            scriptSrc += '&pc=' + encodeURIComponent(this.parentId);
        }
        if (this.topName) {
            scriptSrc += '&tcn=' + encodeURIComponent(this.topName);
        }
        if (this.brand) {
            scriptSrc += '&b=' + encodeURIComponent(this.brand);
        }
        return scriptSrc;
    }
}

function r3_cart(RR_entity) {
    var r3_entity = r3_common(RR_entity);
    this.addItemId = r3_entity.addItemId;
    this.addItemIdCentsQuantity = rr_addItemIdCentsQuantity;
    this.addItemIdDollarsAndCentsQuantity = rr_addItemIdDollarsAndCentsQuantity;
    this.addItemIdPriceQuantity = rr_addItemIdPriceQuantity;
    this.createScript = function(scriptSrc) {
        if (this.purchasesCents) {
            scriptSrc += '&ppc=' + encodeURIComponent(this.purchasesCents);
        }
        if (this.purchasesDollarsAndCents) {
            scriptSrc += '&pp=' + encodeURIComponent(this.purchasesDollarsAndCents);
        }
        if (this.quantities) {
            scriptSrc += '&q=' + encodeURIComponent(this.quantities);
        }
        if (this.purchasesPrice) {
            scriptSrc += '&pp=' + encodeURIComponent(this.purchasesPrice);
        }
        return scriptSrc;
    }
}

function r3_addtocart(RR_entity) {
    var r3_entity = r3_common(RR_entity);
    this.addItemIdToCart = r3_entity.addItemIdToCart;
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_purchased(RR_entity) {
    this.addItemId = rr_addItemIdCentsQuantity;
    this.addItemIdCentsQuantity = rr_addItemIdCentsQuantity;
    this.addItemIdDollarsAndCentsQuantity = rr_addItemIdDollarsAndCentsQuantity;
    this.addItemIdPriceQuantity = rr_addItemIdPriceQuantity;
    this.setOrderNumber = function(orderNumber) {
        this.orderNumber = orderNumber;
    };
    this.createScript = function(scriptSrc) {
        if (this.orderNumber) {
            scriptSrc += '&o=' + encodeURIComponent(this.orderNumber);
        }
        if (this.purchasesCents) {
            scriptSrc += '&ppc=' + encodeURIComponent(this.purchasesCents);
        }
        if (this.purchasesDollarsAndCents) {
            scriptSrc += '&pp=' + encodeURIComponent(this.purchasesDollarsAndCents);
        }
        if (this.quantities) {
            scriptSrc += '&q=' + encodeURIComponent(this.quantities);
        }
        if (this.purchasesPrice) {
            scriptSrc += '&pp=' + encodeURIComponent(this.purchasesPrice);
        }
        return scriptSrc;
    }
}

function r3_search(RR_entity) {
    var r3_entity = r3_common(RR_entity);
    this.addItemId = r3_entity.addItemId;
    this.setBrand = rr_setBrand;
    this.setTerms = r3_entity.addSearchTerm;
    this.createScript = function(scriptSrc) {
        if (this.brand) {
            scriptSrc += '&b=' + encodeURIComponent(this.brand);
        }
        return scriptSrc;
    }
}

function r3_home(RR_entity) {
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_dlp(RR_entity) {
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_error(RR_entity) {
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_myrecs(RR_entity) {
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_personal(RR_entity) {
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_merchandised(RR_entity) {
    var r3_entity = r3_common(RR_entity);
    this.addItemId = r3_entity.addItemId;
    this.setName = rr_setName;
    this.createScript = function(scriptSrc) {
        if (this.name) {
            scriptSrc += '&n=' + encodeURIComponent(this.name);
        }
        return scriptSrc;
    }
}

function r3_wishlist(RR_entity) {

    var r3_entity = r3_common(RR_entity);
    this.addItemId = r3_entity.addItemId;
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_generic(RR_entity) {
    this.setPageTypeId = rr_setPageTypeId;
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_landing(RR_entity) {
    this.isValid = function() {
        return true;
    };
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_ensemble(RR_entity) {
    this.addCategoryId = rr_addCategoryId;
    this.setId = rr_setId;
    this.setRecommendable = rr_setRecommendable;
    this.createScript = function(scriptSrc) {
        if (this.categoryIds) {
            scriptSrc += '&cis=' + encodeURIComponent(this.categoryIds);
        }
        if (this.id) {
            scriptSrc += '&p=' + encodeURIComponent(this.id);
        }
        if (typeof this.recommendable != RR_entity.U) {
            scriptSrc += '&re=' + encodeURIComponent(this.recommendable);
        }
        return scriptSrc;
    }
}

function r3_registry(RR_entity) {
    var r3_entity = r3_common(RR_entity);
    this.setRegistryId = r3_entity.setRegistryId;
    this.createScript = function(scriptSrc) {
        return scriptSrc;
    }
}

function r3_addtoregistry(RR_entity) {
    var r3_entity = r3_common(RR_entity);
    this.setRegistryId = r3_common.setRegistryId;
    this.addItemIdCentsQuantity = rr_addItemIdCentsQuantity;
    this.addItemIdDollarsAndCentsQuantity = rr_addItemIdDollarsAndCentsQuantity;
    this.addItemIdPriceQuantity = rr_addItemIdPriceQuantity;
    this.addAlreadyAddedItemId = function(id) {
        if (typeof this.alreadyAddedRegistryItemIds == RR_entity.U) {
            this.alreadyAddedRegistryItemIds = '';
        }
        this.alreadyAddedRegistryItemIds += '|' + id;
    };
    this.createScript = function(scriptSrc) {
        if (this.alreadyAddedRegistryItemIds) {
            scriptSrc += '&aari=' + encodeURIComponent(this.alreadyAddedRegistryItemIds);
        } else if (r3_entity.itemIds) {
            scriptSrc += '&aari=' + encodeURIComponent(r3_entity.itemIds);
        }
        if (this.purchasesCents) {
            scriptSrc += '&ppc=' + encodeURIComponent(this.purchasesCents);
        }
        if (this.purchasesDollarsAndCents) {
            scriptSrc += '&pp=' + encodeURIComponent(this.purchasesDollarsAndCents);
        }
        if (this.purchasesPrice) {
            scriptSrc += '&pp=' + encodeURIComponent(this.purchasesPrice);
        }
        if (this.quantities) {
            scriptSrc += '&q=' + encodeURIComponent(this.quantities);
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