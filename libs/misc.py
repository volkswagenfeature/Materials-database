

class button_grid:
    """
    A object that draws a grid of un-clickable buttons, which can be set to
    different colors. It is used to display the the status of a batch of
    pages in the download quene as they update and complete. NOTE: there is
    no seperate function to draw the grid. It draws itself on instantiation
    within the currently selected cell.

    Args:
        iterator (iterator): Used to create the buttons, and give them
        appropriate labels. These same labels are used as keys to update
        the buttons, so they must be suitable for this purpouse.

    Attributes:
        buttonlist (dict): Used to store the objects that reference the buttons

    """
    # Used for a good-looking display/diagnostic system 
    from IPython import display as dis
    import ipywidgets as ipw
    
    def __init__(self, iterator):

        self.buttonlist = dict()
        for i in iterator:
            newbut = ipw.Button(value=True,
                                description=str(i),
                                layout=ipw.Layout(width='42px', height='25px'),
                                disabled=True)
            self.buttonlist[i] = newbut
        container = ipw.Box(tuple(self.buttonlist.values()))
        container.layout.flex_flow = "row wrap"
        dis.display(container)

    def setval(self, index, value):
        """
        A method required by all display systems. Responsible for
        setting the item at index to value. In this case, index
        comes from the iterator, and value is any css specified
        color keyword.
        
        Args:
            index (int): Technicaly any hashable, but I only used
            integers. The index of the button in the button grid
            you want to change the color of. 
            
            value (string): The css specified color you want to 
            set the selected button to.
        """
        self.buttonlist[index].style.button_color = value
        

