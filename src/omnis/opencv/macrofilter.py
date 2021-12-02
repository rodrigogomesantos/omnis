import numexpr as ne
import numpy as np
import colorsys
import math
import cv2

class objeto():
    def __init__(self, center, id, dots, area, rects, rectangle):
        self.area = area
        self.rectangle = rectangle
        self.dots = dots
        self.rects = rects
        self.center = center
        self.id = id

class Manipulator():
    def __init__(self, gcode_encoder):
        self.gcode = gcode_encoder

    def catch(self):
        pass

    def latch(self):
        pass

    def move(self, *args, **kwargs):
        self.gcode.M_G0(*args, *kwargs)
        pass

    def reset(self):
        pass

    def feedrate(self):
        pass

class Filter():
    def __init__(self, name, colorRange, areaRange, kernel_A, kernel_B, mode, method):
        self.name = name
        self.colorRange = colorRange
        self.areaRange = areaRange
        self.kernel_A = kernel_A.kernel
        self.kernel_B = kernel_B.kernel
        self.mode = mode
        self.method = method

def makeFilter(name, filters_data):
    model = filters_data["filters"][name]
    # for name, model in filters_data["filters"]:
    color_name = model['colors']['name']
    color_mode = model['colors']['mode']
    color_lower = filters_data['colors'][color_name][color_mode]["lower"]
    color_upper = filters_data['colors'][color_name][color_mode]["upper"]

    colorange = colorRange(color_name, color_mode, color_lower, color_upper)

    area_name = model['areas']['name']
    area_lower = filters_data['areas'][area_name]['min']
    area_upper = filters_data['areas'][area_name]['max']
    area_scales = filters_data['areas'][area_name]['scales']

    arearange = areaRange(area_lower, area_upper, area_scales)

    kernel_A = Kernel(**filters_data["kernels"][model['kernels']['A']])
    kernel_B = Kernel(**filters_data["kernels"][model['kernels']['B']])
    mode = filters_data["retrieval_algorithm"][model["mode"]]
    method = filters_data["approximation_methods"][model["methods"]]
    return {name:Filter(name, colorange, arearange, kernel_A, kernel_B, mode, method)}

class cor():
    def __init__(self, value, mode):
        self.mode = mode
        if self.mode == 'hex':
            self.hex = value
            self.rgb = self.hex2int(value)
            self.hsv = self.rgb2hsv(*self.rgb)
            self.cv2_hsv = [self.hsv[0], (self.hsv[1]*255)/100, (self.hsv[2]*255)/100]
        elif self.mode == "rgb":
            self.rgb = value
            self.hex = self.any2hex(value)
            self.hsv = self.rgb2hsv(*self.rgb)
            self.cv2_hsv = [self.hsv[0], (self.hsv[1]*255)/100, (self.hsv[2]*255)/100]
        elif self.mode =="hsv":
            self.hsv = value
            self.rgb = self.hsv2rgb(*self.hsv)
            self.hex = self.any2hex(self.rgb)
            self.cv2_hsv = [self.hsv[0], (self.hsv[1]*255)/100, (self.hsv[2]*255)/100]
        elif self.mode =='cv2_hsv':
            self.cv2_hsv = value
            self.hsv = [self.cv2_hsv[0], (self.cv2_hsv[1]*100)/255, (self.cv2_hsv[2]*100)/255]
            self.rgb = self.hsv2rgb(*self.hsv)
            self.hex = self.any2hex(self.rgb)
            

    def getColor(self, mode):
        return getattr(self, mode)

    def hsv2rgb(self, h, s_, v_):
        s = s_/100
        v = v_/100
        c = v*s
        x = c*(1-abs(math.fmod( h/60.0, 2)- 1));
        m = v-c
        if 0 <= h < 60:
            r,g,b = c,x,0
        elif 60 <= h < 120:
            r,g,b = x,c,0
        elif 120 <= h < 180:
            r,g,b = 0, c, x
        elif 180 <= h < 240:
            r,g,b = 0, x, c
        elif 240 <= h < 300:
            r,g,b = x, 0, c
        else:
            r,g,b = c, 0, x
        return (int((r+m)*255), int((g+m)*255), int((b+m)*255))
    
    def rgb2hsv(self, r, g, b):
        #rgb normal: range (0-255, 0-255, 0.255)
        red=r
        green=g
        blue=b
        #get rgb percentage: range (0-1, 0-1, 0-1 )
        red_percentage= red / 255
        green_percentage= green / 255
        blue_percentage=blue / 255

        #print(red_percentage, green_percentage, blue_percentage)
        #get hsv percentage: range (0-1, 0-1, 0-1)
        color_hsv_percentage=colorsys.rgb_to_hsv(red_percentage, green_percentage, blue_percentage) 
        #print('color_hsv_percentage: ', color_hsv_percentage)

        #get normal hsv: range (0-360, 0-255, 0-255)
        color_h=round(360*color_hsv_percentage[0])
        color_s=round(100*color_hsv_percentage[1])
        color_v=round(100*color_hsv_percentage[2])
        #print(color_hsv)
        color_hsv=(color_h, color_s, color_v)
        print("hsv:",color_hsv)
        return color_hsv

    def any2hex(self, hsv_):
        return  tuple(map(hex, hsv_))

    def hex2int(self, hex_):
        return  tuple(map(lambda x: int(x, 16),hex_))
        
class colorRange():
    def __init__(self, name, mode, lower, upper):
        self.name= name
        self.lower = cor(lower, mode)
        self.upper = cor(upper, mode)
        self.mode = mode
    def get(self, mode):
        return {
            "lower":self.lower.getColor(mode),
            "upper":self.upper.getColor(mode),
        }
    def getFull(self):
        return {
            self.name:{
            "hex":self.get("hex"),
            "rgb":self.get("rgb"),
            "hsv":self.get("hsv"),
            }
        }

class areaRange():
    def __init__(self, min, max, scales):
        self.unit = next((key for key, value in scales.items() if value == 1), 'undefined')
        self.min = min
        self.max = max
        self.createRanges(scales)
    def createRanges(self, scales):
        for unit, scale in scales.items():
            setattr(self, f"range_{unit}", {unit:{"min":self.min*scale, "max":self.max*scale}})

    def getRange(self, **kw):
        if kw.get('unit'):
            return getattr(self, f"range_{kw.get('unit')}")
        else: return {self.unit:{"min":self.min, "max":self.max}}

class Kernel():
    def __init__(self, sizes=[3,3], type="float32", number="ones", divisor=1, explicit=False):
        self.sizes = sizes
        self.type = type
        self.number = number
        self.divisor = divisor
        if explicit:
            self.kernel = np.array(explicit)
        else:
            self.kernel = getattr(np, self.number)((self.sizes[0], self.sizes[1]), getattr(np, type)) / self.divisor

class identificador():
    def __init__(self, filter_name, filter_config, template_match={}):
        self.config = makeFilter(filter_name, filter_config)[filter_name]
        self.imagem = None
        self.mask = None
        self.data = None
        self.template = template_match
        #self.identify()

    def updateImg(self, newFrame)-> None:
        self.imagem  = newFrame
        #cv2.imshow("newFrame", self.imagem )
        #cv2.waitKey(1)

    def updateFilter(self, newFitler) -> None:
        self.config = newFitler

    def identify(self)-> dict:
        output = []
        self.data, self.mask = self.apply(self.imagem, self.config)
        for indx , info in enumerate(self.data):
            obj = objeto(info['center'], indx, info['dots'], info['area'], info['rects'], info['rectangle'])
            if self.validateObject(self.template, obj.__dict__):
                output.append(obj)
        return output
    
    def validateObject(self, math_template, template):
        for k, v in math_template.items():
            if isinstance(v, dict):
                if not self.validateObject(v, template[k]):
                    return False
            elif isinstance(v, list) and isinstance(v[0], list):
                for _id, _v in enumerate(v):
                    if not eval(f"{_v.replace('_value_', str(template[k][_id]))}"):
                        return False
            elif not eval(f"{v.replace('_value_', str(template[k]))}"):
                return False
        return True

    def findContour(self, image, filter_obj) -> dict:
        contours, hierarchy = cv2.findContours(image, mode=getattr(cv2, filter_obj.mode), method=getattr(cv2, filter_obj.method))
        #cv2.imshow("Processimg", image)
        self.data = []
        try:
            hierarchy = hierarchy[0]
        except TypeError:
            return self.data
        for component in zip(contours, hierarchy):
            currentContour = component[0]
            area = cv2.contourArea(currentContour)
            template = {}
            areas = filter_obj.areaRange.getRange(unit='px')['px']
            if areas['min'] < area < areas['max']:
    
                template["area"] = area

                xA, yA, wA, hA = cv2.boundingRect(currentContour)
                template["rectangle"] = ((xA, yA), (wA, hA))

                boxA = np.int0(cv2.boxPoints(cv2.minAreaRect(currentContour)))
                
                sortedBoxX =sorted(boxA, key=lambda x: x[0])
                sortedBoxY =sorted(boxA, key=lambda x: x[1])
                A,B,C,D = tuple(sortedBoxX[0]), tuple(sortedBoxX[-1]), tuple(sortedBoxY[0]), tuple(sortedBoxY[-1])

                AB = (abs(A[0]-B[0])**2+abs(A[1]-B[1])**2)**0.5
                AC = (abs(A[0]-C[0])**2+abs(A[1]-C[1])**2)**0.5
                AD = (abs(A[0]-D[0])**2+abs(A[1]-D[1])**2)**0.5
                # M =  (int((abs(A[0]-B[0])/2)+A[0]), int((abs(C[1]-D[1])/2)+C[1]))
                # template["center"] = M
                
                template["dots"] = {'A':A, 'B':B, 'C':C, 'D':D}
                template["rects"] = {'AB':AB, 'AC':AC, 'AD':AD}

                momentsA = cv2.moments(currentContour)
                cxA = int(momentsA["m10"] / momentsA["m00"])
                cyA = int(momentsA["m01"] / momentsA["m00"])
                template["center"] = (cxA, cyA)
                
                self.data.append(template)
        return self.data 


    def HSVMask(self, img, config):
        color_range  = config.get('cv2_hsv')
        return cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL), np.array(color_range['lower']), np.array(color_range['upper']))
    # Reduz ruídos os ruidos da mascara.
    def refineMask(self, maskToRefine, kernel_A, kernel_B):
        return cv2.morphologyEx(
               cv2.morphologyEx(maskToRefine, cv2.MORPH_CLOSE, kernel_A),
                                              cv2.MORPH_OPEN,  kernel_B)

    def apply(self, img, config, **kwargs):
        #print(config)
        hsvmask = self.HSVMask(img, config.colorRange)
        #cv2.imshow("hsvmask", hsvmask)
        bettermask = self.refineMask(hsvmask, config.kernel_A, config.kernel_B)
        cnts = self.findContour(bettermask, config)
        return cnts, bettermask

class AreaProcessing():
    def __init__(self, name, cam_obj, config, identificador, **kwargs):
        self.name = name
        self.cam = cam_obj
        self.config = config[name]
        self.world = self.cam.getFrame()
        self.world2draw = self.world.copy()
        self.identifier = identificador
        self.data = []
        self.stopped = False
        self.kw = kwargs
        self.blur = self.kw.get('blur')
    def process(self, **kwargs) -> dict:
        self.data = []
        self.world = cv2.blur(self.cam.getFrame(), self.blur) if self.blur else self.cam.getFrame()
        self.world2draw = self.world.copy()

        if kwargs.get('autoColor'):
            for color_area in self.areaCutter("color_coordinate", self.world):
                img_color, dots_color = color_area[1], color_area[0]
                _min, _max = self.defineColor(img_color)
                self.identifier.config.colorRange.lower = cor(_min, 'cv2_hsv')
                self.identifier.config.colorRange.upper = cor(_max, 'cv2_hsv')

        for areas_info in self.areaCutter("obj_coordinate", self.world):
            
            img, dots = areas_info[1], areas_info[0]
            # img_color, dots_color = color_info[1], color_info[0]
            # img, dots = cuts_info[1], cuts_info[0]

            # if kwargs.get('autoColor'):
            #     min, max = self.defineColor(img_color)
            #     self.identifier.config.colorRange.lower = cor(min, 'cv2_hsv')
            #     self.identifier.config.colorRange.upper = cor(max, 'cv2_hsv')
            
            self.identifier.updateImg(img)
            objects = self.identifier.identify()
            self.data.append(objects)

            if kwargs.get('drawData'):
                self.drawData(img, dots, dots_color, objects)
        return self.data

    def drawData(self, cut, insert_points, color_base_points, obj_list):
        rgb_base =(150,70,70)
        rgb_base_img = np.zeros([cut.shape[0], cut.shape[1], 3], np.uint8)
        for c in range(0,3):
            rgb_base_img[:, :, c] = np.zeros([cut.shape[0], cut.shape[1]]) + rgb_base[c]
        
        
        imgg= cv2.bitwise_or(cut, cut, None, self.identifier.mask)
        bkg = cv2.bitwise_or(rgb_base_img, rgb_base_img, None, cv2.cv2.bitwise_not(self.identifier.mask))

        img = cv2.bitwise_or(imgg, bkg)
        cv2.imshow('gg',imgg)
        cv2.imshow('bk',bkg)
        cv2.imshow('img_or',img)
 
        cv2.waitKey(1)
        for objeto in obj_list:

            for k, v in objeto.rects.items():
                id = list(objeto.rects.keys()).index(k)
                bgr=((255,50,50), (50,255,50), (50,50,255))
                cv2.line(img, objeto.dots[k[0]], objeto.dots[k[1]], bgr[id], 2)
                txt = f"[{k}]: "+str(round(v,2))
                txts = cv2.getTextSize(text=txt, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, thickness=2)[0]
                cv2.putText(img, txt, (objeto.center[0],objeto.center[1]+id*(txts[1]+5)) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, bgr[id], 2)
            cv2.putText(img, str(objeto.id), (objeto.center[0]-50,objeto.center[1]) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

            
            cv2.drawMarker(img, objeto.center, (255,255,255))
            for k, v in objeto.dots.items():
                cv2.putText(img, str(k), tuple(v), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)


        self.world2draw[
            insert_points[0][1]:insert_points[1][1],
            insert_points[0][0]:insert_points[1][0]
            ] = img

        # Desenha 5px fora da area de definição de cor
        cv2.rectangle(self.world2draw, tuple(color_base_points[0]), tuple(color_base_points[1]), (0, 0,0), 2)

    def areaCutter(self, what, image):
        cuts = []
        a = [
                [
                    [
                        dots + self.config[what]["origins"][index][pos] for pos, dots in enumerate(dots_tuple)
                    ]for dots_tuple in square_dots
                ]for index, square_dots in enumerate(self.config[what]["squares"])
            ]
        for dots_group in a:
            cuts.append(
                (
                    dots_group,
                    image[
                        dots_group[0][1]:dots_group[1][1],
                        dots_group[0][0]:dots_group[1][0]
                    ]
                )
            )
        return cuts

    def defineColor(self, img_color):
         # procura na amostra de cor, a cor dominante
        rgb_base = self.rgbDominantColor(img_color)
        
        # cria uma imagem de amostra que contenha somente a cor dominante
        rgb_base_img = np.zeros([200, 200, 3], np.uint8)
        for c in range(0,3):
            rgb_base_img[:, :, c] = np.zeros([200, 200]) + rgb_base[c]

        # converte a amosta de cor dominante pra hsv
        hsv_bkg = cv2.cvtColor(rgb_base_img, cv2.COLOR_BGR2HSV_FULL)

        #acha os valores correspondentes em hsv tirando uma média de toda a imagem (como é feita de uma cor só, a média é a conversão direta)
        hsv_bkg_median = np.mean(np.array(hsv_bkg), axis=(1,0)).tolist()
        
        # cria um range minimo  máximo usando a média - n% ('n%' é definido pelo objeto)
        hsv_bkg_median_max = list(map(lambda x: x+(x*self.config["accuracy_range"]), hsv_bkg_median))
        hsv_bkg_median_min = list(map(lambda x: x-(x*self.config["accuracy_range"]), hsv_bkg_median))


        return hsv_bkg_median_min, hsv_bkg_median_max
  
    def rgbDominantColor(self, a):
        a2D = a.reshape(-1,a.shape[-1])
        col_range = (256, 256, 256) # generically : a2D.max(0)+1
        eval_params = {'a0':a2D[:,0],'a1':a2D[:,1],'a2':a2D[:,2],
                    's0':col_range[0],'s1':col_range[1]}
        a1D = ne.evaluate('a0*s0*s1+a1*s0+a2',eval_params)
        return np.unravel_index(np.bincount(a1D).argmax(), col_range)
    
    def stop(self):
        self.stopped = True

    def stream(self):
        while not self.stopped:
            self.process(autoColor=True, drawData=True)
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'
                        + cv2.imencode('.JPEG', self.world2draw,
                                        [cv2.IMWRITE_JPEG_QUALITY, 100])[1].tobytes()
                        + b'\r\n')
